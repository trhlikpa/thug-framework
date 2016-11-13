#!/bin/bash
set -e

if [ "$1" = 'uwsgi' ]; then
	chown -R web .
	exec uwsgi "${@:2}"
fi

exec "$@"