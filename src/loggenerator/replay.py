import json
import os
import ijson
import time
from datetime import datetime
import requests

LOGS_DIRECTORY = "./flaws_cloudtrail_logs"
dd_api_key = ""
dd_app_key = ""
batch_size = 1

print("logreplay is starting.")

def replay(): 
    logfiles = os.listdir(path=LOGS_DIRECTORY)
    logfiles.sort()
    print(str(len(logfiles)) + " logfiles found. starting replay...")
    iteration = 1
    logs_sent = 0
    for logfile in logfiles: 
        print("Starting replay of " + logfile)
        fh = open(LOGS_DIRECTORY + "/" + logfile)
        logs = ijson.items(fh, 'Records.item')

        for log in logs: 
            batch = []
            # we need to set a current timestamp in the log
            # format: 2017-02-12T19:59:10Z
            current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            log['eventTime'] = current_time
            #print(log)

            url = 'https://http-intake.logs.datadoghq.com/api/v2/logs?ddtags=source'
            headers = {
                'content-type': 'application/json', 
                'DD-API-KEY': dd_api_key,
                'DD-APPLICATION-KEY': dd_app_key
            }

            payload = {
                "ddsource": "cloudtrail",
                "service": "cloudtrail",
                "message": log
            }

            batch.append(payload)
            logs_sent = logs_sent + 1
            
            if logs_sent % batch_size == 0:
                r = requests.post(url, headers=headers, json=batch)
                print(r)
                print("{s} logs published".format(s = logs_sent))
                #time.sleep(1)
    iteration = iteration + 1
    print("finished iteration {s}".format(s = iteration))

while(True): 
    replay()
