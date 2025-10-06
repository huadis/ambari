#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

## Runs superset as a daemon
## Environment Variables used by this script -
## SUPERSET_CONFIG_DIR - directory having superset config files
## SUPERSET_LOG_DIR - directory used to store superset logs
## SUPERSET_PID_DIR - directory used to store pid file

usage="Usage: superset.sh (start|stop|status)"

if [ $# -le 0 ]; then
  echo $usage
  exit 1
fi

command=$1

BIN_DIR="${SUPERSET_BIN_DIR:-/usr/bigtop/current/superset/bin}"
CONF_DIR="${SUPERSET_CONFIG_DIR:-/etc/superset/conf}"
LOG_DIR="${SUPERSET_LOG_DIR:-/var/log/superset}"
PID_DIR="${SUPERSET_PID_DIR:-/var/run/superset}"

GROUP="${SUPERSET_GROUP:-hadoop}"
USER="${SUPERSET_USER:-superset}"

BIND_ADDRESS="${SUPERSET_BIND_ADDRESS:-0.0.0.0}"
PORT="${SUPERSET_PORT:-9088}"

PID_FILE="${PID_DIR}/${SUPERSET_PID_FILE:-superset.pid}"
ACCESS_LOG_FILE="${LOG_DIR}/${SUPERSET_ACCESS_LOG_FILE:-superset-access.log}"
ERROR_LOG_FILE="${LOG_DIR}/${SUPERSET_ERROR_LOG_FILE:-superset-error.log}"
LOG_LEVEL="${SUPERSET_LOG_LEVEL:-info}"
WORKERS="${SUPERSET_WORKERS:-4}"
WORKER_CLASS="${SUPERSET_WORKER_CLASS:-gthread}"
THREADS="${SUPERSET_THREADS:-20}"
GUNICORN_TIMEOUT="${SUPERSET_TIMEOUT:-60}"
GUNICORN_KEEPALIVE="${SUPERSET_KEEPALIVE:-2}"
WORKER_MAX_REQUESTS="${SUPERSET_MAX_REQUESTS:-0}"
WORKER_MAX_REQUESTS_JITTER="${SUPERSET_MAX_REQUESTS_JITTER:-0}"
SERVER_LIMIT_REQUEST_LINE="${SUPERSET_SERVER_LIMIT_REQUEST_LINE:-0}"
SERVER_LIMIT_REQUEST_FIELD_SIZE="${SUPERSET_SERVER_LIMIT_REQUEST_FIELD_SIZE:-0}"

FLASK_APP="${SUPERSET_FLASK_APP:-superset.app:create_app()}"

# pid=$PID_DIR/superset.pid

case $command in
  (start)

    if [ -f ${PID_FILE} ]; then
      if kill -0 `cat ${PID_FILE}| head -n 1` > /dev/null 2>&1; then
        echo Superset node running as process `cat ${PID_FILE} | head -n 1`.  Stop it first.
        exit 1
      fi
    fi

    ${SUPERSET_BIN_DIR}/gunicorn \
      --daemon \
      --reload \
      --group "${GROUP}" \
      --user "${USER}" \
      --bind "${BIND_ADDRESS}:${PORT}" \
      --pid "${PID_FILE}" \
      --access-logfile "${ACCESS_LOG_FILE}" \
      --error-logfile "${ERROR_LOG_FILE}" \
      --log-level "${LOG_LEVEL}" \
      --workers ${WORKERS} \
      --worker-class ${WORKER_CLASS} \
      --threads ${THREADS} \
      --timeout ${GUNICORN_TIMEOUT} \
      --keep-alive ${GUNICORN_KEEPALIVE} \
      --max-requests ${WORKER_MAX_REQUESTS} \
      --max-requests-jitter ${WORKER_MAX_REQUESTS_JITTER} \
      --limit-request-line ${SERVER_LIMIT_REQUEST_LINE} \
      --limit-request-field_size ${SERVER_LIMIT_REQUEST_FIELD_SIZE} \
      "${FLASK_APP}"

    echo "Started Superset"
    ;;

  (stop)

    if [ -f ${PID_FILE} ]; then
      TARGET_PID=`cat ${PID_FILE} | head -n 1`
      if kill -0 $TARGET_PID > /dev/null 2>&1; then
        echo Stopping process `cat ${PID_FILE} | head -n 1`...
        kill $TARGET_PID
      else
        echo No superset node to stop
      fi
      rm -f ${PID_FILE}
    else
      echo No superset node to stop
    fi
    ;;

   (status)
    if [ -f ${PID_FILE} ]; then
      if kill -0 `cat ${PID_FILE} | head -n 1` > /dev/null 2>&1; then
        echo RUNNING
        exit 0
      else
        echo STOPPED
      fi
    else
      echo STOPPED
    fi
    ;;

  (*)
    echo $usage
    exit 1
    ;;
esac
