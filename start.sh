#!/bin/bash
gunicorn3 --workers=2 ohmyrss.wsgi:application -b 0.0.0.0:8090 --worker-class gevent --reload -D