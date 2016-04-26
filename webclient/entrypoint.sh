#!/bin/bash
set -e

if [ "$1" = 'python' ]; then
	chown -R user .
	exec python "${@:2}"
fi

exec "$@"