#!/usr/bin/env python
# coding: utf-8


import json
import requests
import shutil
import os

os.chdir('/home/ubuntu/TextProcessing/data');
file1 = open("status.txt","r+")  
text =file1.read()

webhook_url = 'https://hooks.slack.com/services/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'
slack_data = {'text': text }

response = requests.post(
    webhook_url, data=json.dumps(slack_data),
    headers={'Content-Type': 'application/json'}
)
if response.status_code != 200:
    raise ValueError(
        'Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text)
    )

shutil.os.remove('status.txt')







