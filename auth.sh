#!/bin/sh
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
unset AWS_ACCESS_KEY_ID
eval $(python auth.py "$@")

