#!/bin/bash
# build deb and rpm
# resolve links - $0 may be a softlink
PRGDIR=$(cd `dirname $0`; pwd)
cd ${PRGDIR}

PYENV_PATH="/opt/pyenv"
ENV_NAME="myapp"
APP_NAME="myapp-api"
PROJECT_NAME="myapp"
LOCAL_PATH="/usr/local/bin"

while getopts "a:d:c:f:e:h:i:k:m:o:p:r:s:u:v:" arg; do
    case $arg in
     a) a=$OPTARG ;;
     d) d=$OPTARG ;;
     c) c=$OPTARG ;;
     f) f=$OPTARG ;;
     h) echo "Usages: "
        echo "  -a package_prefix_name  -d pkg_dir ;"
        echo "  -h help_info -i arch -k ver_key -m ver_min  ;"
        echo "  -p suffix  -r arch_info  -s scp_dir -u authors -v version ;"
        exit 0    ;;
     i) i=$OPTARG ;;
     k) k=$OPTARG ;;
     m) m=$OPTARG ;;
     o) o=$OPTARG ;;
     p) p=$OPTARG ;;
     r) r=$OPTARG ;;
     s) s=$OPTARG ;;
     u) u=$OPTARG ;;
     v) v=$OPTARG ;;
     ?) echo "Unknown argument"; exit 1; ;;
    esac
done
shift $(($OPTIND - 1))

function set_env() {
    [ x$a != x ] && DEB_PREFIX_NAME=$a || DEB_PREFIX_NAME=myapp
    [ x$d != x ] && DEB_BUILD_DIR=$d || DEB_BUILD_DIR=build-deb
    [ x$f != x ] && OUT_DIR=$f || OUT_DIR="/tmp/cstack"
    [ x$o != x ] && SYSTEM_TYPE=$o || SYSTEM_TYPE=debian
    [ x$c != x ] && COMPILE_SO=$c || COMPILE_SO=0
    [ x$i != x ] && ARCH=$i || ARCH=amd64
    [ x$k != x ] && VER_KEY=$k || VER_KEY=0.0.1
    [ x$m != x ] && VER_MIN=$m || VER_MIN=local
    [ x$p != x ] && SUFFIX=$p || SUFFIX=deb
    [ x$r != x ] && RELEASE=$r || RELEASE=dailybuild
    [ x$s != x ] && SCP_DIR=$s || SCP_DIR="deber1@release-server:/home/download/xview/${VER_KEY}/${RELEASE}/${APP_NAME}/"
    [ x$u != x ] && AUTHORS=$u || AUTHORS="xiaobin.zhao<xiaobin.zhao@cstack.io>"
    [ x$v != x ] && VERSION=$v || VERSION=${VER_KEY}-${VER_MIN}
    PKG_NAME=${DEB_PREFIX_NAME}_${VERSION}_${ARCH}.${SUFFIX}
    export PKG_CONFIG_PATH=/usr/share/pkgconfig:/usr/lib64/pkgconfig
}

set_env

function build_process() {
    cd ${PRGDIR}
    cd ..

    # 将版本信息,写入version.txt
    touch version.txt
    echo ${VERSION} > version.txt

    # 清理历史构建目录
    /bin/rm -rf ${DEB_BUILD_DIR}

    # 创建目录
    /bin/mkdir -p ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}

    chmod +x ./*.sh
    ./myapp.sh install  # 执行安装poetry和项目依赖

    # 安装编译所用的cython,调用编译加密
    if [ "${COMPILE_SO}" -eq 1 ]; then
        ${PYENV_PATH}/${ENV_NAME}/bin/python3 -m pip install cython==3.0.6
        ${PYENV_PATH}/${ENV_NAME}/bin/python3 build/compile.py myapp/
    fi

    # 复制 python virtualenv
    /bin/cp -rf ${PYENV_PATH} ${DEB_BUILD_DIR}/opt

    # 创建目录
    /bin/mkdir -p ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}
    /bin/mkdir -p ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/resources
    /bin/mkdir -p ${DEB_BUILD_DIR}/lib/
    /bin/mkdir -p ${DEB_BUILD_DIR}${LOCAL_PATH}
    /bin/mkdir -p ${DEB_BUILD_DIR}/usr/

    # 复制版本信息，模块信息
    /bin/cp -rf ./version.txt ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/
    /bin/cp -rf ./*.sh ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/
    /bin/cp -rf ./poetry.lock ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/
    /bin/cp -rf ./pyproject.toml ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/

    # 复制文件
    if [ "${COMPILE_SO}" -eq 1 ]; then
        /bin/cp -rf ./compile_dist/xview ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/  # 复制编译后的文件
        /bin/rm -fr ./compile_dist  # 清理多余的 compile_dist 目录
    fi

    if [ "${COMPILE_SO}" -eq 0 ]; then
        /bin/cp -rf ./${PROJECT_NAME} ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/  # 复制源文件
    fi

    /bin/cp -rf ./DEBIAN ${DEB_BUILD_DIR}/
    /bin/cp -rf ./etc ${DEB_BUILD_DIR}/
    /bin/cp -rf ./lib/systemd ${DEB_BUILD_DIR}/lib/


    # 修改 control 文件
    sed 's/${VERSION}/'"${VERSION}"'/g' DEBIAN/control > ${DEB_BUILD_DIR}/DEBIAN/control

    # 脚本赋予可执行权限
    chmod +x ${DEB_BUILD_DIR}/DEBIAN/postinst
    chmod +x ${DEB_BUILD_DIR}/DEBIAN/postrm
    chmod +x ${DEB_BUILD_DIR}/DEBIAN/preinst
    chmod +x ${DEB_BUILD_DIR}/DEBIAN/prerm
    chmod +x ${DEB_BUILD_DIR}/opt/${PROJECT_NAME}/${APP_NAME}/*.sh

    # 清理多余的 .git 目录
    find ${DEB_BUILD_DIR} -name .git | xargs -i /bin/rm -fr {}

    # 清理 test 目录
    find ${DEB_BUILD_DIR} -name test | xargs -i /bin/rm -fr {}

    # 清理多余的 __pycache__ 目录
    find ${DEB_BUILD_DIR} -name __pycache__ | xargs -i /bin/rm -fr {}
}
# 构建deb
function make_deb() {
    dpkg-deb -b ${DEB_BUILD_DIR} ${PKG_NAME}

    # 清理构建目录
    /bin/rm -rf ${PYENV_PATH}
    /bin/rm -rf ${DEB_BUILD_DIR}
    /bin/cp  ${PKG_NAME}  ./build
    /bin/rm -f  ${PKG_NAME}

    # 清理版本信息，模块信息
    echo "build ${APP_NAME} ${VERSION} success"
}

#构建rpm
function make_rpm() {
    cd ${PRGDIR}
    cd ..
    rm -rf $OUT_DIR
    /bin/mkdir -p $OUT_DIR
    # 清理构建目录
    /bin/rm -rf ${PYENV_PATH}

    # 清理版本信息，模块信息
    /bin/rm -f version.txt
    rm -rf $HOME/rpmbuild
    mkdir -p $HOME/rpmbuild/SPECS
    mkdir -p $HOME/rpmbuild/SOURCES
    mkdir -p $HOME/rpmbuild/BUILDROOT
    mkdir -p $HOME/rpmbuild/RPMS
    mkdir -p $HOME/rpmbuild/SRPMS
    mkdir -p ${APP_NAME}-${VERSION}
    tar -zcf $HOME/rpmbuild/SOURCES/${APP_NAME}-${VERSION}.tar.gz ${APP_NAME}-${VERSION}
    pwd
    mv ${DEB_BUILD_DIR}/usr/lib ${DEB_BUILD_DIR}/usr/lib64
    mv ${DEB_BUILD_DIR}/lib ${DEB_BUILD_DIR}/usr/

    preinst=`cat ${DEB_BUILD_DIR}/DEBIAN/preinst`
    postinst=`cat ${DEB_BUILD_DIR}/DEBIAN/postinst`
    prerm=`cat ${DEB_BUILD_DIR}/DEBIAN/prerm`
    postrm=`cat ${DEB_BUILD_DIR}/DEBIAN/postrm`
    eval "cat <<EOF
    $(< ./build/myapp.spec.template)
    EOF
    "  > myapp.spec
    rm -rf ${DEB_BUILD_DIR}/DEBIAN
    cp -rf ${DEB_BUILD_DIR} $OUT_DIR/
    cp myapp.spec $HOME/rpmbuild/SPECS/
    #rm -f myapp.spec
    rpmbuild -bb --nodeps --nosignature  $HOME/rpmbuild/SPECS/myapp.spec

    # 清理构建目录
    /bin/cp -f $HOME/rpmbuild/RPMS/x86_64/*.rpm ./build/
    /bin/rm -rf ${PYENV_PATH}
    /bin/rm -rf ${DEB_BUILD_DIR}
}

#上传tag build 的包
function push_rpm_pkg() {
  echo "scp"
    #scp  $HOME/rpmbuild/RPMS/x86_64/*.rpm  $SCP_DIR
#    ssh ${SCP_DIR%%:*} "cd ${SCP_DIR##*:} ; [ -f ${PKG_NAME} ] && md5sum  ${PKG_NAME} | tee ${PKG_NAME}.txt"
}

function push_deb_pkg() {
    scp ./build/${PKG_NAME}  ${SCP_DIR}
}

if [ $SYSTEM_TYPE = "centos" ]
then
    build_process
    make_rpm
    push_rpm_pkg
elif [ $SYSTEM_TYPE = "debian" ]
then
    build_process
    make_deb
    push_deb_pkg
else
	exit 0
fi