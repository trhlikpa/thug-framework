#!/bin/bash
set -e

if [ "$1" = 'celery' ]; then
	chown -R user .
	exec celery "${@:2}"
fi

exec "$@"