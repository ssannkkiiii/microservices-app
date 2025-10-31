#!/bin/sh
export PORT=${PORT:-80}
envsubst '$$PORT' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
exec nginx -g "daemon off;"
