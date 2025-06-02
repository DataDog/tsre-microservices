import json
import os
import ijson
import time
from datetime import datetime
import requests
import logging

logger = logging.getLogger("loggenerator")
logging.basicConfig(level=logging.DEBUG)

LOGS_DIRECTORY = os.getenv("REPLAY_LOGS_DIR", ".") # this is where we will look for the JSON log files
BATCH_SIZE = int(os.getenv("REPLAY_BATCH_SIZE", "1")) # this controls how many logs we send at once to Datadog
SLEEP_TIME = int(os.getenv("REPLAY_SLEEP_TIME", "1")) # this controls how long we sleep before reading the next message from the JSON file
logger.debug("Config dump: batch_size={}, sleep_time={}, logs_dir={}".format(BATCH_SIZE, SLEEP_TIME, LOGS_DIRECTORY))

dd_api_key = os.getenv("DD_API_KEY", None) 
dd_app_key = os.getenv("DD_APP_KEY", None)
if dd_api_key is None or dd_app_key is None: 
    logger.fatal("Could not find an API key or APP key to send data to Datadog. Quitting.")
    exit(255)

logger.info("Log Replay is starting.")

def replay(): 
    logfiles = os.listdir(path=LOGS_DIRECTORY)
    logfiles.sort()
    logger.info("{} logfiles found. starting replay...".format(len(logfiles)))
    iteration = 1
    logs_sent = 0
    for logfile in logfiles: 
        if logfile.endswith(".json"):
            logger.info("Starting replay of logfile {}".format(logfile))
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
                
                if logs_sent % BATCH_SIZE == 0:
                    r = requests.post(url, headers=headers, json=batch)
                    logger.info("{} logs published".format(logs_sent))
                    time.sleep(SLEEP_TIME)
    iteration = iteration + 1
    logger.info("finished iteration {s}".format(s = iteration))

while(True): 
    replay()
