#!/usr/bin/env bash 

gunicorn src.chatapp.main:app -k \
 uvicorn.workers.UvicornWorker --bind "0.0.0.0:8003" \
 --workers 1 --timeout 60 --graceful-timeout 45 --preload \
 --keep-alive 10 --access-logfile /dev/null --error-logfile - \
 --log-level "warning"