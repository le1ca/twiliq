import twilio, json, os, sys

""" This script is provided to help clean up Media resources from your Twilio
    account that are no longer present in the queue.
    
    It works as follows:
    
    1. Your twiliQ config file is loaded and the state file is opened.
    2. Your Twilio account is accessed to find all message-related media files.
    3. Any media files that are present in your Twilio account but not still in
       the twiliQ queue will be deleted.
       
    You can run the script with the "--dry" parameter to do a dry run (nothing
    will actually be deleted). With this option set, all of the files which
    would normally be deleted will be listed on stdout instead.
    
    Use this script at your own risk -- it may be buggy, and if that's the case,
    it can delete all of your Twilio media.
"""

def main(conf_file, dry=False):
        # load twiliQ config
        config = json.load(open(conf_file, 'r'))
        
        # if this isn't a dry run, ask the user if they know what they're doing
        if not dry:
                print("This script might delete all your media.")
                sure = raw_input("Are you sure you want to do this? [y/n] ")
                if not sure.lower() == "y":
                        return
                print("")
        
        # set up REST client
        client = twilio.rest.TwilioRestClient(
                config['twilio']['account'],
                config['twilio']['token']
        )
        
        # load twiliQ queue
        queued = []
        statefile = os.path.expanduser(config['twiliq']['statefile'])
        data = json.load(open(statefile, 'r'))
        for _, media_list in data['queue']:
                if not isinstance(media_list, list):
                        media_list = [media_list]
                queued.extend(media_list)
        queued = set(queued)
        print("Have %d queued media items." % len(queued))
        print("")
        
        # load messages from Twilio
        print("Gathering list of messages...")
        messages = list(client.messages.iter())
        print("Found %d messages." % len(messages))
        print("")
        
        # load media from Twilio
        print("Gathering list of media...")
        media = []
        for m in messages:
                try:
                        media.extend(list(m.media_list.iter()))
                except twilio.TwilioRestException:
                        pass
        print("Found %d media." % len(media))
        print("")
        
        # compute the set difference and do the thing
        diff = [m for m in media if not m.uri in queued]
        print("Deleting %d media items..." % len(diff))
        for m in diff:
                if dry:
                        print(m.uri)
                else:
                        m.delete()
        print("Done.")
        

if __name__ == "__main__":
        if len(sys.argv) < 2 or len(sys.argv) > 3:
                print("usage: %s <config_file> [--dry]" % sys.argv[0])
                sys.exit(0)
        main(sys.argv[1], (len(sys.argv) > 2 and sys.argv[2] == "--dry"))
