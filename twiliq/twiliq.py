from twilio_wrapper import twilio_wrapper
from twilio import TwilioRestException
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
                if len(media_list) == 0:
                        logging.info("Got message with no attachments")
                        return
                with lock:
                        for media_type, url in media_list:
                                data['queue'].append((body, url))
                                logging.info("Added message: (%s, %s)" % (body, url))
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
                if send_now:
                        try:
                                with lock:
                                        body, url = data['queue'].pop(0)
                                        json.dump(data, open(statefile, 'w'))
                                        logging.info("Transmitting: (%s, %s)" % (body, url))
                                        tw.mms(config['twiliq']['recipients'], body, url)
                        except IndexError as e:
                                logging.warning("Tried to transmit, but queue is empty")
                        except TwilioRestException as e:
                                logging.error("Error transmitting message to Twilio")
                                logging.exception(e)
                        except Exception as e:
                                logging.error("Unhandled exception")
                                logging.exception(e)
                sleeper[0] = threading.Timer(
                        config['twiliq']['period'],
                        tick,
                        ()
                )
                sleeper[0].start()
        
        # start sleeper
        tick(False)
        
        # start listener
        app = tw.get_listener()
        app.run(host=config['twiliq']['listen'], port=config['twiliq']['port'])
