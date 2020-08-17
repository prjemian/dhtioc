#!/bin/bash

# manage the IOC for dhtioc

#--------------------
# change the program defaults here
DEFAULT_SESSION_NAME=dhtioc
DEFAULT_IOC_PREFIX=${HOSTNAME}:
#--------------------

SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}
SELECTION=${1:-usage}
SESSION_NAME=${DEFAULT_SESSION_NAME}
IOC_PREFIX=${DEFAULT_IOC_PREFIX}

IOC_BINARY=dhtioc
IOC_OPTIONS="--list-pvs"
IOC_OPTIONS+=" --prefix ${IOC_PREFIX}"
START_IOC_COMMAND="${IOC_BINARY} ${IOC_OPTIONS}"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if [ -z "$IOC_STARTUP_DIR" ] ; then
    # If no startup dir is specified, use the directory with this script
    IOC_STARTUP_DIR=$(dirname "${SHELL_SCRIPT_NAME}")
fi

# echo "SESSION_NAME = ${SESSION_NAME}"
# echo "IOC_PREFIX = ${IOC_PREFIX}"
# echo "START_IOC_COMMAND = ${START_IOC_COMMAND}"
# echo "SHELL_SCRIPT_NAME = ${SHELL_SCRIPT_NAME}"
# echo "IOC_STARTUP_DIR = ${IOC_STARTUP_DIR}"
export SCREEN=/usr/bin/screen

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

function checkpid() {
    MY_UID=$(id -u)
    # # The '\$' is needed in the pgrep pattern to select vm7, but not vm7.sh
    IOC_PID=$(pgrep "${IOC_BINARY}"\$ -u "${MY_UID}")
    # #!echo "IOC_PID=${IOC_PID}"

    if [ "${IOC_PID}" != "" ] ; then
        # Assume the IOC is down until proven otherwise
        IOC_DOWN=1
        SCREEN_PID=""

        # At least one instance of the IOC binary is running;
        # Find the binary that is associated with this script/IOC
        for pid in ${IOC_PID}; do
            # compare directories
            BIN_CWD=$(readlink "/proc/${pid}/cwd")
            IOC_CWD=$(readlink -f "${IOC_STARTUP_DIR}")

            if [ "$BIN_CWD" = "$IOC_CWD" ] ; then
                # The IOC is running;
                # the process with PID=$pid is the
                # IOC that was run from $IOC_STARTUP_DIR
                P_PID=$(ps -p "${pid}" -o ppid=)
                # strip leading (and trailing) whitespace
                arr=($P_PID)
                P_PID=${arr[0]}
                SCREEN_SESSION="${P_PID}.${SESSION_NAME}"
                SCREEN_MATCH=$(${SCREEN} -ls "${SCREEN_SESSION}" | grep "${SESSION_NAME}")
                if [ "${SCREEN_MATCH}" != "" ] ; then
                    # IOC is running in screen
                    IOC_DOWN=0
                    IOC_PID=${pid}
                    SCREEN_PID=${P_PID}
                    break
                fi
            fi
        done
    else
        # IOC is not running
        IOC_DOWN=1
    fi

    return ${IOC_DOWN}
}

function checkup () {
    if ! checkpid; then
        echo "# $(date --iso-8601=seconds)"
        restart
        # run
        echo "# $(date --iso-8601=seconds) $(${SCREEN} -ls)"
        # sleep 10
        # echo "# $(date --iso-8601=seconds) ${IOC_PREFIX}counter=$(caproto-get ${IOC_PREFIX}counter)"
        # sleep 2
    fi
}

function console () {
    if checkpid; then
        echo "Connecting to ${SCREEN_SESSION}'s screen session"
        # The -r flag will only connect if no one is attached to the session
        #!screen -r "${SESSION_NAME}"
        # The -x flag will connect even if someone is attached to the session
        ${SCREEN} -x "${SCREEN_SESSION}"
    else
        echo "${SCREEN_NAME} is not running"
    fi
}

function exit_if_running() {
    # ensure that multiple, simultaneous IOCs are not started by this user ID
    MY_UID=$(id -u)
    IOC_PID=$(pgrep "${SESSION_NAME}"\$ -u "${MY_UID}")

    if [ "" != "${IOC_PID}" ] ; then
        echo "${SESSION_NAME} IOC is already running (PID=${IOC_PID}), won't start a new one"
        exit 1
    fi
}

function restart() {
    stop
    start
}

function run_ioc() {
    # only use this for diagnostic purposes
    exit_if_running
    ${START_IOC_COMMAND}
}

function screenpid() {
    if [ -z "${SCREEN_PID}" ] ; then
        echo
    else
        echo " in a screen session (pid=${SCREEN_PID})"
    fi
}

function start() {
    if checkpid; then
        echo -n "${SCREEN_SESSION} is already running (pid=${IOC_PID})"
        screenpid
    else
        echo "Starting ${SESSION_NAME} with IOC prefix ${IOC_PREFIX}"
        cd "${IOC_STARTUP_DIR}"
        # Run SESSION_NAME inside a screen session
        CMD="${SCREEN} -dm -S ${SESSION_NAME} -h 5000 ${START_IOC_COMMAND}"
        ${CMD}
    fi
}

function status() {
    if checkpid; then
        echo -n "${SCREEN_SESSION} is running (pid=${IOC_PID})"
        screenpid
    else
        echo "${SESSION_NAME} is not running"
    fi
}

function stop() {
    if checkpid; then
        echo "Stopping ${SCREEN_SESSION} (pid=${IOC_PID})"
        kill "${IOC_PID}"
    else
        echo "${SESSION_NAME} is not running"
    fi
}

function usage() {
    echo "Usage: $(basename "${SHELL_SCRIPT_NAME}") {start|stop|restart|status|checkup|console|run}"
    echo ""
    echo "    COMMANDS"
    echo "        console   attach to IOC console if IOC is running in screen"
    echo "        checkup   check that IOC is running, restart if not"
    echo "        restart   restart IOC"
    echo "        run       run IOC in console (not screen)"
    echo "        start     start IOC"
    echo "        status    report if IOC is running"
    echo "        stop      stop IOC"
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

case ${SELECTION} in
    start) start ;;
    stop | kill) stop ;;
    restart) restart ;;
    status) status ;;
    checkup) checkup ;;
    console) console ;;
    run) run_ioc ;;
    *) usage ;;
esac
