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

PYENV_PATH=$(/root/.poetry/bin/poetry debug|grep Path|awk '{print $2}')

${PYENV_PATH}/bin/alembic -c myapp/db/migrations/alembic.ini $@


exit 0
