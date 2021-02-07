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

# pydantic 管理参数校验和OpenAPI在线文档

## pydantic的schema model和db 的model共享描述字段

1. SQLAlchemy ORM 添加数据库描述字段

   有2个字段可以作为描述字段：

   1. doc：只是在python侧做文档描述，不进入DB
   2. comment: 创建表时，会把该字段写入SQL

   可以知道我们使用comment会更合适

2. pydantic的schema model 每个字段都有description字段，最后会生成在线文档的字段描述字段。那么是否可以只写一次该描述文字，就可以在DB和schema都可以看到呢？研究发现，还是自己实现吧。

   通过查看FastAPI的源码，可以知道在FastAPI实例初始化时就会进行schema model的解析并且生成openapi.json文件。所以普通的继承和重写是不能实现的，python有一神器：metaclass。

   ```
   MetaClass元类，本质也是一个类，但和普通类的用法不同，它可以对类内部的定义（包括类属性和类方法）进行动态的修改。可以这么说，使用元类的主要目的就是为了实现在创建类时，能够动态地改变类中定义的属性或者方法。
   ```

   自定义SchemaMetaclass,实现对schema model 类创建时，把db model的comment字段的value设置到 schema model的description字段。

   1. schema model必须添加参数，可以知道从那个 DB model查找comment。这里使用 Config.orm_model属性
   2. 有可能schema model存在继承关系，所以查找需要递归查找Config.orm_model属性
   3. scheme model的所有字段的定义需要设置Filed()定义
   4. 之后可以继续优化，比如自动设置默认值和字符串最长（max_length）

## OpenAPI在线文档管理
定制openAPI 文档。

- 抽出OpenAPI文档全局设置参数

- 使用本地swagger-ui文件

- 提供加载静态文件路由

  ```python
  # main.py
  from fastapi import FastAPI
  from fastapi.staticfiles import StaticFiles
  from myapp.openapi import custom_openapi
  
  
  app = FastAPI(docs_url=None, redoc_url=None)  # docs url 重新定义
  custom_openapi(app)  # 设置自定义openAPI
  
  app.mount("/static", StaticFiles(directory="myapp/static"), name="static")
  ```

  ```python
  # openapi.py
  
  from fastapi.openapi.utils import get_openapi
  from fastapi.openapi.docs import (
      get_redoc_html,
      get_swagger_ui_html,
      get_swagger_ui_oauth2_redirect_html,
  )
  
  
  OpenAPISchema = {
      "title": "My app",
      "version": "1.0.0",
      "description": "python web framework base on FastAPI.",
      "openapi_tags": [{
          "name": "desktop",
          "description": "Manage desktops."
      }]
  }
  
  
  def custom_openapi(app):
      """
      重新定义swagger的一些参数，包括文档全局设置（title/version等）以及使用本地静态资源。
      """
      def my_openapi():
          if app.openapi_schema:
              return app.openapi_schema
          openapi_schema = get_openapi(
              title=OpenAPISchema["title"],
              version=OpenAPISchema["version"],
              description=OpenAPISchema["description"],
              routes=app.routes,
              tags=OpenAPISchema["openapi_tags"]
          )
          app.openapi_schema = openapi_schema
          return app.openapi_schema
  
      app.openapi = my_openapi
  
      @app.get("/docs", include_in_schema=False)
      async def custom_swagger_ui_html():
          return get_swagger_ui_html(
              openapi_url=app.openapi_url,
              title=OpenAPISchema["title"] + " - Swagger UI",
              oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
              swagger_js_url="/static/swagger-ui-bundle.js",
              swagger_css_url="/static/swagger-ui.css",
              swagger_favicon_url="/static/favicon.ico"
          )
  
      @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
      async def swagger_ui_redirect():
          return get_swagger_ui_oauth2_redirect_html()
  
      @app.get("/redoc", include_in_schema=False)
      async def redoc_html():
          return get_redoc_html(
              openapi_url=app.openapi_url,
              title=OpenAPISchema["title"] + " - ReDoc",
              redoc_js_url="/static/redoc.standalone.js",
              redoc_favicon_url="/static/favicon.ico"
          )
  ```


# alembic 管理数据库版本
alembic 是一个做数据库版本管理的工具。
 1. 配置文件位于: {PROJECT_NAME}/db/migrations/alembic.ini 会自动获取配置文件里关于db的设置
 2. 配置项主要为：`sqlalchemy.url = mysql+pymysql://xview:xview@localhost:3306/xview?charset=utf8`
 3. 生成增量版本: `alembic revision --autogenerate -m "2.0.3"' # 2.0.3 是message，标记本次升级的描述
 4. 升级到最新版本: `alembic upgrade head'  
 5. 升级到 下一个 版本: `alembic upgrade +1`
 6. 打印升级到最新版本的 SQL 脚本: `alembic upgrade head --sql` 
 7. 降级到 前一个 版本: `alembic downgrade -1`

## 设置 db url

修改alembic的env.py文件，设置db url为项目的配置文件中设置的url

```python
def run_migrations_online():
    # .... 一些代码省略...
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.db.url},  # 使用dynaconf文件的配置替换alembic.ini的配置
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)
    # .... 一些代码省略...

```

# 框架定制 

## 逻辑分层

架构设计的本质是：降本增效。分层可以进行一定程度的逻辑隔离，各司其职，简化开发流程，便于维护，实现降本增效。

1. schema（资源）层：本层在java等体系中称之为VO（View Object），用于展示层，作用是把前端展示的数据进行封装。在这里，我称之为视图层或者资源层。这一层会把API的response的数据结构进行控制。因为python是弱类型语言，response可以随意修改其数据结构，所以定义一个数据结构进行显示控制，很有必要。

   资源是RestFul风格的API强调的一个概念。这个资源应该是针对业务进行的抽象对象，与数据库设计的表可能是一一对应，也可能是1个资源对应多个表。比如一个学生资源，可能会包含学生的基本信息（姓名、性别、年龄等）和课程信息（科目、分数等）；学生信息和课程信息在数据库会是2个表，但是在资源上是一个。

   资源层的schema class会设置 每个字段的属性（类型、长度、正则等）以及必填等，这些校验项会在API层对request/response数据进行校验。

   资源层对应的数据结构会在API层进行填充。

   本层的实现技术基于pydantic。

2. API层：处理入参和出参校验。进行入/出参的参数校验，包括必填（选填）参数、参数类型（数字、字符串、枚举等）、参数限制（长度、大小氛围、正则等）等；以及url的设置，http method，http response code等。

   这一层还可以有一些中间件或者说是拦截器等的组件来进行一些请求前或者请求后的操作，比如：请求前的token校验、权限校验等；请求后的异常处理和消息通知等

   API层会关注response的组成结果，实例化资源层定义的资源对象。每个资源一般会定义一个或者多个第三层的数据模型（数据库表）。

   本层的实现技术基于fastAPI。

3. 业务层：经过API层过滤之后，进入业务层的数据一定是符合预期的，规范的；这样可以进行相应的业务处理，比如一个订单请求，在这一层可能涉及到的有订单数据生成、减库存、购物车数据变动等等。

   1. 得到的数据是符合预期的，规范的
   2. 业务层应该专注于业务处理，不必关注数据怎么入库
   3. 业务层需要暴露一些接口给其他业务层调用
   4. 不同的业务模块应该且最好只能通过业务层的接口进行互相import和调用
   5. 业务层的方法应多使用SOLID设计模式

   本层的技术实现没有明确定义。

4. 数据/模型层：这一层定义了数据字典或者称之为数据结构，并且和数据库连接（DBAPI）连通，进行数据的入库操作。这一层应该无关业务只有数据。数据库连接应该随用随放，不要持有太久；注意SQL优化等。

   本层的技术实现基于sqlalchemy。

  ## db

使用db_writer和db_reader进行装饰器封装，以达到数据库立刻执行和立刻关闭session。

  ## exception

exception和正常的response进行封装成统一的返回格式：

```json
{
  "data": {},
  "message": "message.",
  "code": "API_200_000_9999"
}
```

##  error_code

```txt
code有4部分组成，中间以_分割，比如：API_200_000_9999
第一部分：字符串，标识是API类型还是其他类型。目前只有API,未来可能有SOCKET等其他类型
第二部分：3位，HTTP code， 比如200，400，500
第三部分：3位，业务编号，比如000标识系统统一编号，001标识桌面，002标识用户
第四部分：4位，错误码，比如0000标识未知错误，0001标识参数校验失败
```

  ## token

这里不使用OAuth2的token方案。因为OAth2的token方案相对复杂，且考虑到与第三方对接。尤其token refresh的过程：
1. login得到access_token 和 refresh_token,refresh_token比access_token的有效期更长
2. 客户端请求使用access_token，如果过期，客户端使用refresh_token再次请求得到新的access_token。
   当然这里也可以返回新的refresh_token，新的refresh_token可以有新的过期时间
3. 如果access_token过期，并且refresh_token也过期，那么需要重新登录。

以上方案略显复杂。重新设计如下：
1. login得到access_token。
   token的生成方式有多种，比如jwt;非对称加密字符串；但是 jwt加密字符串过长且jwt本身的方案特性本系统没有采用；
   非对称AES加密又消耗时间过长，经验证加密一个字符串需要500ms左右。这行的话login API的耗时要达到1s,太长。所以简化为：
   生成带有uuid的字符串，然后使用base64加密得到token。这样token可以保持唯一性（因为uuid），也可以在客户端反解出来得到token
   的内容；

2. 客户端使用access_token请求，成功之后，会更新过期时间,token不变，新的过期时间为当前时间+有效时长（默认5分钟）

3. 只要客户端一直请求（请求之间间隔最长不超过5分钟），那么token就一直有效

此方案优点：

1. token请求之后，在不间断操作下会一直有效，不用客户端不断refresh
2. 逻辑简单
3. token包含了一些信息，可以进行解密读取

缺点：
1. 需要保存会话信息，即需依赖redis这样的server端存储token和其过期时间点

  ## 公共类库

  - lock
  - cache
  - tools工具包
      - UUID
      - md5
      - Symmetric Encryption、Symmetric Decryption 对称加密解密
      - format_datetime 时间格式转化
      - 使用python执行一些系统命令
      - 使用socket判断`ip:port `是否可用
      - ip和数字互转
      - 随机字符串生成
      - 获取本地ip/mac

  ## 单元测试

使用fastapi的 test client进行http请求。

在项目根目录，比如`/root/workspace/fastAPI/`目录下执行 `pytest`即可执行单元测试。

# 打包发布

poetry build 即可得到wheel 包



# 扩展

基础框架搭建好之后，自然要啦考虑到怎么做扩展。

## 数据模型和数据查询

## schema 模型

## api 接口

## manager 业务



  

  

