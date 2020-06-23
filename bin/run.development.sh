#!/bin/bash
git add .
git commit -m "Update"
git pull origin master
ps aux | grep 'start_translate_sentiment.py' | grep -v grep | awk '{print $2}' | xargs kill
ps aux | grep 'start_temporal_processing.py' | grep -v grep | awk '{print $2}' | xargs kill
nohup /usr/bin/env python3 /home/mygetzu/projects/holly-sentiment-with-translator/start_translate_sentiment.py > /tmp/listener.log 2>&1 &
