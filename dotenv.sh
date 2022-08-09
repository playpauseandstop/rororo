#!/bin/bash
#
# Load env vars from dotenv files before running actual commands.
#

function dotenv () {
    dotenv_name=${1}
    set -a;
    if [ -f "${dotenv_name}" ]; then
        if [ -z "${DOTENV_QUIET}" ]; then
            echo "[dotenv.sh] Loading ${dotenv_name}..."
        fi
        # shellcheck source=/dev/null
        source "${dotenv_name}"
    fi
    set +a;
}

STAGE=${STAGE:-dev}
PWD=$(pwd)

for dotenv_name in "./.env.${STAGE}.local" "./.env.${STAGE}" "./.env.local" "./.env"; do
    if [ -f "${dotenv_name}" ]; then
        dotenv "${dotenv_name}"
        break
    fi
done

exec "$@"
