# twiliQ
Twilio app that enqueues MMS content received, then sends it out to recipients
at a specified interval.

## What it does

TwiliQ listens for incoming MMS from authorized numbers, and adds those MMS
to an internal queue. Every once in a while (as often as you configure), the
first MMS in the queue will be popped off and sent to all of the recipients you
have specified.

## Setup

To use this app, you first need to create a config file. The provided file, 
example.config.json, will make a good starting point.

In the "twilio" section, you need to fill in your API credentials (AccountSID
and AuthToken) as well as the number you want to use for outgoing MMS.

In the "twiliq" section, you have to specify a whitelist (list of numbers that
are allowed to submit MMS to the queue), a list of receipients (who will receive
the enqueued MMS), and a period (in minutes, which specifies how often a message
will be sent from the queue). You must also specify a path for the state file
(where twiliQ will store its queue in case it needs to restart) as well as the
interface and port which you want to listen on.

To run twiliQ, simply invoke the twiliq package and provide your config file as
the first argument (e.g., python twiliq config.json).

## Disclaimer

I have not tested this app very thoroughly. It was created solely for me to send
a bunch of cat pictures to my girlfriend, even while I'm asleep. If you find any
problems, please let me know, but do not expect me to fix them. I might update
TwiliQ, or I might not. If you fix it yourself and submit a pull request, I will
almost certainly merge your code.

Also, I am not responsible for TwiliQ eating up all of your Twilio funds if it
bugs out or you configure it improperly. Use at your own risk.
