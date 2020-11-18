#!/usr/bin/env bash
#set -x

GREEN="\\033[1;32m"
DEFAULT="\\033[0;39m"
RED="\\033[1;31m"

# Getting CWD where bash script resides
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DASH_HOME="${DIR}"
SCREEN_NAME="Snake_Oil_Crypto_Window"

cd ${DASH_HOME}

#if [ -e "${DIR}/sage-8.9/local/bin/python" ]; then
if [ -e "${DIR}/SageMath/local/bin/python3" ]; then
	echo "Sage virtualenv seems to exist."
	ENV_LAUNCH="sage --python3 ${DIR}/SageMath/local/bin/rq worker"
else
	echo "Please make sure you have a sage environment installed, exiting."
	exit 1
fi

PID_SCREEN=$(screen -ls | grep ${SCREEN_NAME} | cut -f2 | cut -d. -f1)
if [[ $PID_SCREEN ]]; then
	echo -e $RED"* A screen '$SCREEN_NAME' is already launched"$DEFAULT
	echo -e $GREEN"Killing $PID_SCREEN"$DEFAULT;
	kill $PID_SCREEN
else
	echo 'No screen detected'
fi

screen -dmS ${SCREEN_NAME}

ps auxw |grep 'rq worker' |grep -v grep ; check_rq_worker=$?

sleep 0.1
if [ "${check_rq_worker}" == "1" ]; then
	echo -e $GREEN"\t* Launching rq worker"$DEFAULT
	screen -S ${SCREEN_NAME} -X screen -t "Worker-1" bash -c "${ENV_LAUNCH};"
else
	echo -e $RED"\t* Worker seems to be already running."$DEFAULT
fi
