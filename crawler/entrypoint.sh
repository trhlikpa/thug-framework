#!/bin/bash
set -e

if [ "$1" = 'celery' ]; then
	chown -R crawler .
	exec celery "${@:2}"
fi

exec "$@"