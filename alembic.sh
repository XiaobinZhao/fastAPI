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

POETRY_PATH="/opt/pyenv/myapp"
export PATH="$POETRY_PATH/bin:$PATH"

if ! command -v poetry &> /dev/null; then
    echo "-- poetry 命令未找到，请使用myapp.sh install 安装..."
    exit 1
fi

PYENV_PATH="/opt/pyenv/myapp"

${PYENV_PATH}/bin/alembic -c myapp/db/migrations/alembic.ini $@


exit 0
