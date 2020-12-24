from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="XVIEWCONF",
    settings_files=['./myapp/conf/settings.toml', '/etc/myapp/setting.toml'],
)
