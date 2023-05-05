# HMT-Fetch-Bot

This tool is designed to help students of the Hochschule für Musik und Theater
(HMT) Rostock who are waiting for a rehearsal room. At the moment, they get
a wartenummer (german for waiting number, a buzzword at the HMT, that even all 
the non-german speakers know) on the waiting list and have to manually check
the website of the HMT in order to know when its their turn on the waiting list.
This is in the one hand time consuming and annoying for the individual student
and has the side effect, that they can easily miss their wartenummer, which will
be skipped if you do not report within a few minutes at the entrance, where 
they give out the keys for the rehearsal rooms. And on the other hand, the 
servers of the HMT are unnecessarily flooded with a huge amount of requests
for the webpage that shares the current wartenummer. 

This small telegram-bot automatically fetches the current wartenummer from the 
[HMT-website](https://www.hmt-rostock.de/aktuelles-service/wartenummer/).
Users can register their wartenummer and will get notified by the bot when that 
wartenummer is the current one.  
The bot is run via a raspberry pi. For that, the main.py script is started 
through a systemd service and the raspberry pi itself turns off every evening
at 21:30. Power supply is regulated by a mechanical timer switch, that is used to
automatically turn it back on (and thereby the telegram bot) at 8:00
every day.
