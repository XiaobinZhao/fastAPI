python web framework base on FastAPI.

- http://www.fastapipy.com/
- https://fastapi.tiangolo.com/zh/

# poetry管理包
使用poetry管理python的包依赖和项目隔离。

python和其他语言java/nodejs等一样，都需要进项项目级别的包管理，但是python会有些不同。

1. python 与java/JavaScript等语言的project隔离是不一样的。python的项目依赖包都是统一安装到site-packages目录下，如果不同project依赖了不同版本的同一模块，那么后安装的会卸载掉先安装的。所以python需要为每一个项目进行单独隔离，所以virtualenv应运而生。
2. 那么讨论python的依赖管理一般就指 依赖管理+虚拟环境。最初的工具就是pip+virtualenv，pip用来做包管理，virtualenv用来做虚拟环境。那么就带来问题：
   1. 需要同时使用2个工具
   2. 不能动态更新requirements.txt，这点尤其突出。这种文本格式的文件只能记录依赖包的名称，不能像yaml/json/xml一样记录更多的环境信息和参数。每次更新都是需要手动执行`pip freeze > requirements.txt`，如果那次遗漏，那么后患无穷。
3. 因此，pipenv诞生了。
4. pipenv可以看成是pip+virtualenv两款工具的合体，它集合了pip的依赖包管理和virtualenv虚拟环境 管理于一身。另外，在依赖包记录方面使用Pipfile替代原来的requirements.txt。而且，它能够自动记录并更新记录文件，这样就不在需要手动执行命令来更新requirements.txt。但是他依然有很多缺陷：
   1. Lock速度缓慢
   2. 强行更新不相干依赖
   3. 依赖处理效果较差。
5. `当当~当~当~~~`！Poetry出现了
6. poetry是一款可以管理Python依赖、环境，同時可以用于Python工程打包和发布的一款第三方工具包。poetry通过配置文件pyproject.toml来完成依赖管理、环境配置、基本信息配置等功能。相当于把Python項目中的Pipfile、setup.py、setup.cfg、requirements.txt、MANIFEST.in融合到一起。通过pyproject.toml文件，不仅可以配置依赖包，还可以用于区分开发、测试、生产环境、配置源路径。

poetry 安装会很慢，建议手动下载poetry的安装文件，可以到百度网盘下载（链接: https://pan.baidu.com/s/1Luy4GKYVRHiL9HnKZF_ZBg 提取码: hgac）。下载完成之后，使用`python3.7 get-poetry.py --file poetry-1.1.4-linux.tar.gz` 安装。

- `poetry init` 生成项目配置文件pyproject.toml
- 如果是空的项目，可以使用`poetry create <project_name>`开始
- poetry最低使用python3.7版本
- `poetry add xxxx`，为项目添加依赖包。添加依赖会自动创建virtual env。如果不添加依赖，直接使用env，那么执行`poetry env use <python3.7路径>`，可以使用`whereis python`查询到python3.7的路径
- 得到虚拟环境之后，可以执行`poetry intstall` 安装依赖。
- `poetry show -t`可以查看当前环境安装的依赖，并且显示依赖关系

# dynaconf管理配置文件

## 配置文件类型

python项目的配置文件有多种，比如

- python自带xxx.py文件作为配置文件，比如 Django、flask的setting.py
- 外部的配置文件，通常使用`configparser`库来解析
  - json：在js项目中可能比较常用
  - xml: 其可读性和写法都比较繁琐，基本弃用
  - yaml: 利用空格来定义变量层次结构，更易读；建议使用[Python _Confuse_库](https://github.com/sampsyo/confuse)来解析yaml
  - ini: **ini**文件非常适合较小的项目，但是这些文件仅支持1级深的层次结构
  - conf: 
    - conf其实没有一个固定的标准，比如mysql的配置文件my.cnf其实就是一个ini文件；conf可以是一个ini文件或者其应用能识别的更丰富格式的文件
    - 跟ini一样有些限制
  - toml: 
    - 明确的value类型，不再需要类似`getboolean()`这样测操作才可以获取正确的Value；
    - 支持更丰富的数据类型：**DateTime**，**本地时间**，**数组**，**float**甚至**十六进制值**
    - TOML文件中带括号的部分称为**表**，TOML支持**“嵌套表”**的概念
- 数据库存储配置项
  - mysql
  - redis

以上方案推荐ini/python/toml。

- python文件：
  - 优点：使用简单，配置文件作为一个python的model被import；可以直接在配置文件内使用python的一些语法
  - 缺点：不符合标准项目构建流程，比如linux平台一般配置文件位于/etc目录下
  - 适合项目规模：小型
- conf/ini文件
  - 优点：简单
  - 缺点：只支持一级层次；
  - 适合项目规模：小型
- toml
  - 优点：更丰富的数据类型支持和更多项目元数据配置
  - 缺点：需要支持parse
  - 适合项目规模：全面

**结论：小型项目建议采用conf/ini类型，略复杂项目建议采用toml**。

## conf文件解析库

常用的conf解析类库有：

- python 内置 configparser

  - 可以解析conf、ini文件；写入新的配置

- openstack社区出品oslo.config

  - 解析conf文件；写入新的配置

  - 支持环境变量

  - 支持command-line

  - 支持变量引用，比如

    ```ini
    # (string value)
    rabbit_host = controller
    
    # (integer value)
    rabbit_port = 5672
    
    rabbit_hosts = $rabbit_host:$rabbit_port
    ```
  
- [dynaconf](https://github.com/rochacbruno/dynaconf)

  - 解析多种格式`toml|yaml|json|ini|py`文件；写入配置；默认值；校验
  - 支持环境变量
  - 支持多中开发环境（default, development, testing, production）
  - 内置 **Django** and **Flask** 相关支持
  - 支持cli命令

**结论：推荐使用dynaconf+toml,一步到位**。

## dynaconf使用

1. 添加包依赖`poetry add dynaconf`

2. 在项目应用目录下运行`dynaconf init`,默认生成3个文件

   1. `config.py` 必选文件，我们的应用通过import config来使用配置项
   2.  `.secrets.toml` 可选文件，可以存放一些敏感数据，比如密码、私钥和token等
   3.  `settings.toml `可选文件，配置项文件。一般我们把配置项放到这个文件。dynaconf支持toml|yaml|json|ini(conf)|py等多种格式，建议采用toml。文件格式选型，建议查看上一节。

3. 项目引入settings. 

   ```python
   from dynaconf import Dynaconf
   
   settings = Dynaconf(
       envvar_prefix="DYNACONF",
       settings_files=['settings.toml', '.secrets.toml'],
   )
   ```

   以上是默认生成的config.py. 这里的配置项settings_files指向的`settings.toml`文件是相对于当前执行应用的时候的目录，原文解释如下：

   In the above example, dynaconf will try to load `settings.toml` from the same directory where the program is located, also known as `.` and then will keep traversing the folders in backwards order until the root is located.

   root is either the path where the program was invoked, or the O.S root or the root specified in `root_path`.

   由于是一个相对于**程序执行时**所在的当前目录为查找起始路径，有时候会发现`settings.toml`可能load会出现文件无法正确匹配，导致配置项找不到。所以为了一定可以找到配置项，建议在`settings.toml`后添加一个绝对路径作为备选。当然按照settings_files配置项内容顺序，后边的配置项会覆盖前边的。以下是本程序的示例设置：

   ```python
   from dynaconf import Dynaconf
   
   settings = Dynaconf(
       envvar_prefix="DYNACONF",
       settings_files=['./myapp/conf/settings.toml', '/etc/myapp/settings.toml'],
   )
   ```

4. 配置文件内字符串替换（参数引用）

   settings.toml

   ```toml
   [default]
   db_name = "mydb.db"
   
   [development]
   db_path = "@format {env[HOME]}/{this.current_env}/{env[PROGRAM_NAME]}/{this.DB_NAME}"
   ```

   dynaconf支持 `@format` and `@jinja`2种方式进行字符串替换。jinja需要单独安装依赖包，format内置，相当于python的`str.format`。但是验证下来发现，替换字符串时，必须使用对应配置项的**大写**，如上例。

# loguru管理日志

在 Python 中，一般情况下我们可能直接用自带的 logging 模块来记录日志，包括我之前的时候也是一样。在使用时我们需要配置一些 Handler、Formatter 来进行一些处理，比如把日志输出到不同的位置，或者设置一个不同的输出格式，或者设置日志分块和备份，感觉显得略微繁琐一些。

## loguru

使用[loguru](https://loguru.readthedocs.io/)可以更方便的管理log, loguru有如下feature:

- [Ready to use out of the box without boilerplate](https://loguru.readthedocs.io/en/stable/overview.html#ready-to-use-out-of-the-box-without-boilerplate)  开箱即用，无需配置
- [No Handler, no Formatter, no Filter: one function to rule them all](https://loguru.readthedocs.io/en/stable/overview.html#no-handler-no-formatter-no-filter-one-function-to-rule-them-all) 不需要handler/formatter/filter/function配置，add实现一切
- [Easier file logging with rotation / retention / compression](https://loguru.readthedocs.io/en/stable/overview.html#easier-file-logging-with-rotation-retention-compression) 支持 rotation/retention/压缩
- [Modern string formatting using braces style](https://loguru.readthedocs.io/en/stable/overview.html#modern-string-formatting-using-braces-style) 使用`{}`做字符串替换占位符
- [Exceptions catching within threads or main](https://loguru.readthedocs.io/en/stable/overview.html#exceptions-catching-within-threads-or-main) 捕获程序崩溃和线程内的异常堆栈
- [Pretty logging with colors](https://loguru.readthedocs.io/en/stable/overview.html#pretty-logging-with-colors)  使用 [markup tags](https://loguru.readthedocs.io/en/stable/api/logger.html#color) 支持带颜色显示的logger message
- [Asynchronous, Thread-safe, Multiprocess-safe](https://loguru.readthedocs.io/en/stable/overview.html#asynchronous-thread-safe-multiprocess-safe) 支持异步、线程安全、多进程安全
- [Fully descriptive exceptions](https://loguru.readthedocs.io/en/stable/overview.html#fully-descriptive-exceptions) 更完整的异常堆栈信息（小心暴露你的敏感信息哦）
- [Structured logging as needed](https://loguru.readthedocs.io/en/stable/overview.html#structured-logging-as-needed) 支持json序列化异常对象
- [Lazy evaluation of expensive functions](https://loguru.readthedocs.io/en/stable/overview.html#lazy-evaluation-of-expensive-functions) 延迟赋值
- [Customizable levels](https://loguru.readthedocs.io/en/stable/overview.html#customizable-levels) 支持自定义level
- [Better datetime handling](https://loguru.readthedocs.io/en/stable/overview.html#better-datetime-handling) 更加方便的时间格式设置
- [Suitable for scripts and libraries](https://loguru.readthedocs.io/en/stable/overview.html#suitable-for-scripts-and-libraries) 脚本和第三方库更方便的使用logger
- [Entirely compatible with standard logging](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging) 兼容标准库的logging
- [Personalizable defaults through environment variables](https://loguru.readthedocs.io/en/stable/overview.html#personalizable-defaults-through-en vironment-variables) 通过环境变量来设置个性化参数
- [Convenient parser](https://loguru.readthedocs.io/en/stable/overview.html#convenient-parser) [`parse()`](https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.parse)方法可以方便的解析log日志内容
- [Exhaustive notifier](https://loguru.readthedocs.io/en/stable/overview.html#exhaustive-notifier) 使用[`notifiers`](https://github.com/notifiers/notifiers)组件可以方便的结合loguru实现邮件等方式进行消息通知

OpenAPI

Restfull web服务，其API文档是一个重要的组成部分。FastAPI集成了自动化实现文档的功能，主要的技术实现是基于pydantic进行数据模型等接口定义，然后生成swagger JSON定义文档，结合 [Swagger UI](https://github.com/swagger-api/swagger-ui) 即可得到自动生成的交互式 API 文档，另外还支持 [ReDoc](https://github.com/Rebilly/ReDoc)格式的。

- **Python 3.6 及更高版本**
- 数据校验
- 数据输入/输出类型转换

