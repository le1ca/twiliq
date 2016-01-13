# twiliQ
Twilio app that enqueues MMS content received, then sends it out to recipients
at the specified times.

## What it does

TwiliQ listens for incoming MMS from authorized numbers, and adds those MMS
to an internal queue. Every once in a while (as often as you configure), the
first MMS in the queue will be popped off and sent to all of the recipients you
have specified.

## Setup

The prerequisites for twiliQ are listed in requirements.txt. You can easily
install all of them using "pip -r requirements.txt".

To use this app, you first need to create a config file. The provided file, 
example.config.json, will make a good starting point.

In the "twilio" section, you need to fill in your API credentials (AccountSID
and AuthToken) as well as the number you want to use for outgoing MMS.

In the "twiliq" section, you have to specify a whitelist (list of numbers that
are allowed to submit MMS to the queue), a list of receipients (who will receive
the enqueued MMS), and a cronline which specifies when messages should be sent.
You must also specify a path for the state file (where twiliQ will store its
queue in case it needs to restart) as well as the interface and port which you
want to listen on.

To run twiliQ, simply invoke the twiliq package and provide your config file as
the first argument (e.g., python twiliq config.json). The app does not
automatically daemonize, so you may want to write a wrapper script, or perhaps
run it in a screen.

To receive MMS, you must set up twiliQ such that the HTTP endpoint can be hit
from the Internet. Then, you must log in to Twilio and set the messaging URL for
your number of choice to that of the twiliQ daemon.

## Usage

Each SMS or MMS you send to your Twilio number will be added to the send queue.
Whenever it is time for a message to be sent, the first message will be removed
from the queue and sent to all of the receipients you specified. The messages
you enqueue can contain as many or as little media objects as you'd like, and
they will all be sent exactly as you intended.

At any time, you can send "~STATUS" (without quotes), and twiliQ will reply with
the number of messages that are currently in the queue.

## Disclaimer

I have not tested this app very thoroughly. It was created solely for me to send
a bunch of cat pictures to my girlfriend, even while I'm asleep. If you find any
problems, please let me know, but do not expect me to fix them. I might update
TwiliQ, or I might not. If you fix it yourself and submit a pull request, I will
almost certainly merge your code.

Also, I am not responsible for TwiliQ eating up all of your Twilio funds if it
bugs out or you configure it improperly. Use at your own risk.
