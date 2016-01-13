from twilio_wrapper import twilio_wrapper
from twilio import TwilioRestException
from croniter import croniter
from datetime import datetime, timedelta
import threading, json, logging, os, signal

logging.basicConfig(level=logging.DEBUG)

def main(conf_file):

        # load config
        config = json.load(open(conf_file, 'r'))
        data = {
                'queue': []
        }
        statefile = os.path.expanduser(config['twiliq']['statefile'])
        
        # load state if it exists
        try:
                data = json.load(open(statefile, 'r'))
                logging.info("Existing state loaded - %d entries in queue" % len(data['queue']))
        except IOError:
                logging.info("State file %s does not exist - starting from scratch" % statefile)
                
        # setup for timer thread and synchronization
        lock = threading.Lock()
        sleeper = [None]
        
        # parse cronline
        cron = croniter(config['twiliq']['cronline'], datetime.now())
        
        # interrupt handler to kill sleeper thread
        def interrupt(x, y):
                if sleeper[0]:
                        sleeper[0].cancel()
                raise KeyboardInterrupt
        signal.signal(signal.SIGINT, interrupt)
        
        # incoming mms handler
        def cb(from_num, body, media_list):
                if not from_num in config['twiliq']['whitelist']:
                        logging.info("Incoming message from unlisted number %s" % from_num)
                        return
                if body == "~STATUS":
                        return "Queue contains %d items" % len(data['queue'])
                else:
                        url_list = [url for _,url in media_list]
                        with lock:
                                data['queue'].append((body, url_list))
                                logging.info("Added message: (%s, %s)" % (body, url_list))
                                json.dump(data, open(statefile, 'w'))
        
        # setup twilio client
        tw = twilio_wrapper(
                config['twilio']['account'],
                config['twilio']['token'],
                config['twilio']['number'],
                cb
        )
        
        # sleeper thread timeout routine
        def tick(send_now=True):
        
                # send_now is skipped on the first call to tick()
                if send_now:
                        try:
                                with lock:
                                        body, urls = data['queue'].pop(0)
                                        json.dump(data, open(statefile, 'w'))
                                        # legacy support - if urls is not a list, encapsulate it in a list
                                        if not instanceof(urls, list):
                                                urls = [urls]
                                        logging.info("Transmitting: (%s, %s)" % (body, urls))
                                        tw.mms(config['twiliq']['recipients'], body, urls)
                        except IndexError as e:
                                logging.warning("Tried to transmit, but queue is empty")
                        except TwilioRestException as e:
                                logging.error("Error transmitting message to Twilio")
                                logging.exception(e)
                        except Exception as e:
                                logging.error("Unhandled exception")
                                logging.exception(e)
                
                # figure out when to run next tick - if cron says to run it in
                # the past, just run it now
                delta = max(
                        timedelta(0),
                        cron.get_next(datetime) - datetime.now()
                ).total_seconds()
                
                logging.debug("Next event scheduled in %s seconds" % delta)
                
                # start the timer
                sleeper[0] = threading.Timer(delta, tick, ())
                sleeper[0].start()
        
        # start sleeper
        tick(False)
        
        # start listener
        app = tw.get_listener()
        app.run(host=config['twiliq']['listen'], port=config['twiliq']['port'])
