#!/usr/bin/env bash

# resolve links - $0 may be a softlink
PRG="$0"

while [ -h "$PRG" ]; do
  ls=`ls -ld "$PRG"`
  link=`expr "$ls" : '.*-> \(.*\)$'`
  if expr "$link" : '/.*' > /dev/null; then
    PRG="$link"
  else
    PRG=`dirname "$PRG"`/"$link"
  fi
done

# Get standard environment variables
PRGDIR=`dirname "$PRG"`
cd ${PRGDIR}

APP_NAME="myapp"
POETRY_PATH="/opt/pyenv/myapp"
PID_PATH="/var/run/${APP_NAME}.pid"
LOG_PATH="/var/log/${APP_NAME}"

# poetry安装环境； 使用pip比官方脚本更稳定
export PATH="$POETRY_PATH/bin:$PATH"
# 处理研发环境
# 1. 查找是否有Python3.9；
# 2. 安装poetry
function deal_env() {
    # 检查 python3.9 是否安装
    if ! command -v python3.9 &> /dev/null; then
        echo "Python3.9 未安装，请先安装 Python3.9或者设置Python3.9到PATH"
        exit 1
    else
        echo "-- 使用 Python3.9 运行myapp"
    fi
    # 检查 poetry 命令是否安装
    if ! command -v poetry &> /dev/null; then
        # 如果没有安装，则调用 poetry_install.py 执行安装
        echo "-- 创建pip conf..."
        create_pip_conf

        echo "-- poetry 命令未找到，开始使用pip方式安装..."
        echo "-- 创建poetry运行虚拟环境：${POETRY_PATH}"
        python3.9 -m venv "${POETRY_PATH}"  # 创建 python virtualenv
        $POETRY_PATH/bin/pip install -U pip setuptools
        $POETRY_PATH/bin/pip install poetry

        if [ $? -eq 0 ]; then
          export PATH="$POETRY_PATH/bin:$PATH"
          echo "export PATH=$POETRY_PATH/bin:\$PATH" >> ~/.profile
          echo "-- poetry 安装成功,设置虚拟环境到$POETRY_PATH"
          poetry config virtualenvs.path /opt/pyenv/myapp
          poetry config virtualenvs.create false
        else
          echo "-- poetry 安装失败，请手动接入..."
          exit 1
        fi

    else
        echo "-- poetry 已安装"
        poetry about
    fi

    if [ $? -eq 0 ]; then
      echo "-- myapp 开始安装依赖..."
      poetry install
    else
      echo "-- poetry 安装失败,命令：python3.9 ./build/poetry_install.py"
      exit 1
    fi
}

function create_pip_conf() {
    if [ ! -d "${HOME}/.pip" ]; then
    /bin/mkdir ${HOME}/.pip
    fi
    touch ${HOME}/.pip/pip.conf
    echo "" > ${HOME}/.pip/pip.conf  # 清除文件内容
    # 写入 pip.conf 文件内容
    echo "[global]" >> ${HOME}/.pip/pip.conf
    echo "index-url=https://mirrors.aliyun.com/pypi/simple/" >> ${HOME}/.pip/pip.conf
    echo "[install]" >> ${HOME}/.pip/pip.conf
    echo "trusted-host=mirrors.aliyun.com" >> ${HOME}/.pip/pip.conf
}

function get_setting_key() {
  APP_CONFIG_CMD="${PYENV_PATH}/bin/dynaconf -i myapp.conf.config.settings list --key "
  ${APP_CONFIG_CMD} $1 |grep -v environment|awk '{print $2}'
}

function pre_action() {
    if ! command -v poetry &> /dev/null; then
        # 如果没有安装，则调用 poetry_install.py 执行安装
        echo "-- poetry 命令未找到，请使用 install 安装..."
        exit 1
    fi

    PYENV_PATH=$POETRY_PATH

    # Setting the binding host and port for the service
    BIND_HOST=`get_setting_key "default.host" | sed $'s/\'//g'`
    BIND_PORT=`get_setting_key "default.port"`

    if [ -n ${BIND_HOST} ];then
        HOST=${BIND_HOST}
    fi
    if [ -n ${BIND_PORT} ];then
        PORT=${BIND_PORT}
    fi

    BIND_ADDR="${HOST}:${PORT}"

    if [ ! -d "${LOG_PATH}" ]; then
    mkdir -p "${LOG_PATH}"
    fi
}

function stop()
{
    if [ -f "${PID_PATH}" ]; then
        echo "kill process `cat ${PID_PATH}`"
        kill `cat ${PID_PATH}`
        sleep 2
    fi
}

function start()
{
    pre_action

    # 查看逻辑CPU的个数
    NUM_CORES=`cat /proc/cpuinfo| grep "processor"| wc -l`
    # 使用gunicorn管理Uvicorn进程。使用自定义的worker启动Uvicorn。
    nohup ${PYENV_PATH}/bin/gunicorn myapp.main:app \
        -b ${BIND_ADDR} \
        -w $((NUM_CORES + 1)) \
        -k myapp.worker.MyUvicornWorker \
        --timeout 60 \
        --log-level debug \
        --access-logfile ${LOG_PATH}/app.log \
        --error-logfile ${LOG_PATH}/app.log \
        -p ${PID_PATH} | /usr/bin/cronolog ${LOG_PATH}/app.log &
}

function debug()
{
    pre_action

    # 查看逻辑CPU的个数
    NUM_CORES=`cat /proc/cpuinfo| grep "processor"| wc -l`
    ${PYENV_PATH}/bin/gunicorn myapp.main:app \
        -b ${BIND_ADDR} \
        -w $((NUM_CORES + 1)) \
        -k myapp.worker.MyUvicornWorker \
        --timeout 60 \
        --log-level debug \
        -p ${PID_PATH}
}

function usage()
{
    echo "Usage: ${PRG} ( commands ... )"
    echo "commands:"
    echo "  install      Install ${APP_NAME} dependency packages"
    echo "  start        Start ${APP_NAME} service"
    echo "  debug        Start ${APP_NAME} service in terminal"
    echo "  stop         Stop ${APP_NAME} service"
    echo "  restart      Restart ${APP_NAME} service"
    echo "  status       Show ${APP_NAME} service status"
    echo "  help         Show help"
}

function status()
{
    if [ -f "${PID_PATH}" ]; then
        pid=`cat ${PID_PATH}`  # 获取 pid
        if [ "x${pid}" != "x" ]; then
            c=`ps -ef | grep ${pid} | wc -l`  # 获取 pid 进程数
            if [ "x$c" != "x0" ]; then
                # pid 进程存在
                echo "service ${APP_NAME} is running, pid: ${pid}"
            else
                # pid 进程不存在
                echo "service ${APP_NAME} is stoped"
            fi
        else
            # pid 文件是空的
            echo "service ${APP_NAME} is stoped"
        fi
    else
        # pid 文件不存在
        echo "service ${APP_NAME} is stoped"
    fi
}


case $1 in
    install)
        deal_env
    ;;
    start)
        start
    ;;
    debug)
        debug
    ;;
    stop)
        stop
    ;;
    restart)
        stop
        start
    ;;
    status)
        status
    ;;
    *) usage
    ;;
esac

exit 0
