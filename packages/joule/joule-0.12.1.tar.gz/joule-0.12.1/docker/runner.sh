#!/bin/bash
set -e


# run nginx startup scripts
/bin/sh 15-local-resolvers.envsh
/bin/sh ./20-envsubst-on-templates.sh
/bin/sh ./35-tune-worker-processes.sh

# start nginx
nginx -g "daemon on;"

# start jouled unless --nginx-only is passed
if [ "$1" != "--nginx-only" ]; then
    envsubst < /config/main.template > /config/main.conf
    envsubst < /config/user.template > /config/user.conf
    # append the proxies.conf if it exists
    if [ -f /etc/joule/configs/proxies.conf ]; then
        cat /etc/joule/configs/proxies.conf >> /config/main.conf
    fi
    rm -f /tmp/joule/pid # remove any existing pid (if container restarts)
    /usr/local/bin/jouled    # start jouled
fi
