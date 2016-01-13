from flask import Flask, request, redirect
import twilio.rest, twilio.twiml

class twilio_wrapper:
        """ Wrapper for the Twilio API. Abstracts the functionality we actually
            need, including a Flask server to listen for incoming messages.
        """
        
        def __init__(self, account, token, number, callback):
                """ Constructor
                
                    Requires account ID, auth token, and the phone number
                    we should bind to for sending/receiving. The callback
                    will be hit whenever we receive an MMS.
                """
                self._client = twilio.rest.TwilioRestClient(account, token)     
                self._number = number
                self._cb     = callback
                
        def get_listener(self):
                """ Returns the Flask listener app. Incoming requests will be
                    sent to the registered callback (once the app is started).
                """
                app = Flask(__name__)
                @app.route("/", methods=['GET', 'POST'])
                def msg_listener():
                        from_num = request.values.get('From', None)
                        body = request.values.get('Body', None)
                        media_count = int(request.values.get('NumMedia', None))
                        media_list = [
                                (request.values.get("MediaContentType%d" % i, None),
                                 request.values.get("MediaUrl%d" % i, None)
                                ) for i in range(0, media_count)
                        ]
                        result = self._cb(from_num, body, media_list)
                        resp = twilio.twiml.Response()
                        if result != None:
                                resp.sms(result)
                        return str(resp)
                return app

        def sms(self, recipients, body):
                """ Sends a SMS to the list of recipients
                """
                for recipient in recipients:
                        self._client.messages.create(
                                to    = recipient,
                                from_ = self._number,
                                body  = body
                        )
                
        def mms(self, recipients, body, urls):
                """ Sends the MMS to the list of recipients
                """
                for recipient in recipients:
                        self._client.messages.create(
                                to    = recipient,
                                from_ = self._number,
                                body  = body,
                                media_url = [str(url) for url in urls]
                        )
                
__all__ = ["twilio_wrapper"]
