#!/bin/bash
gunicorn --workers=8 ohmyrss.wsgi:application -b 0.0.0.0:8000 --worker-class gevent --reload -D
