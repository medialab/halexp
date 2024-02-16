#!/bin/sh

export NS=$(cat /etc/resolv.conf | grep nameserver | awk -F" " '{print $2}')

envsubst '\$NS \$BACKEND_HOST \$BACKEND_PORT' < /etc/nginx/nginx-conf.template > /etc/nginx/nginx.conf

exec "$@"
