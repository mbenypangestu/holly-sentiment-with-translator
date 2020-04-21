#!/bin/bash
git add .
git commit -m "Update"
git pull origin master
ps aux | grep 'get_sentiment_degree.py' | grep -v grep | awk '{print $2}' | xargs kill
ps aux | grep 'get_temporal_processing.py' | grep -v grep | awk '{print $2}' | xargs kill
nohup python3 get_sentiment_degree.py &
