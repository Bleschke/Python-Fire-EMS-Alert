# Brian Leschke
# May 24, 2016
# Version 1.0
# Python Fire EMS Alert
# Some code may have been taken from
# other sources.

import imaplib
import email
import os
import RPi.GPIO as GPIO
import time
import pyvona


def extract_body(payload):
    if isinstance(payload,str):
        return payload
    else:
        return '\n'.join([extract_body(part.get_payload()) for part in payload])

conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)
conn.login("USERNAME", "PASSWORD")
conn.select()
typ, data = conn.search(None, 'UNSEEN')
try:

    v = pyvona.create_voice('Access Key', 'Secret Key')
    v.region = 'us-east'
    v.voice_name = 'Salli'
    global FireAlertLED
    FireAlertLED = 26
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(FireAlertLED, GPIO.OUT)
    for num in data[0].split():
        typ, msg_data = conn.fetch(num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                subject=msg['subject']                   
                print(subject)
                payload=msg.get_payload()
                body=extract_body(payload)
                print(body)
		cmd_string = 'mpg123 -q /home/pi/FireAlerts/FireGong.mp3'
		os.system(cmd_string)
		v.speak(body)
		GPIO.output(FireAlertLED,True)	
		time.sleep(120)
		GPIO.output(FireAlertLED,False)	
	    else:
		print('No New Alerts')
        typ, response = conn.store(num, '+FLAGS', r'(\Seen)') 
finally:
    try:
        conn.close()
    except:
        pass
    conn.logout()
