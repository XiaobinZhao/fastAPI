import importlib
import json
import os
import pathlib

from loguru import logger

root_path = pathlib.Path(__file__).parent.parent.resolve()  # 使用绝对路径，防止环境不同导致的异常

path_module = 'myapp.error_code'
base_module = 'myapp.base.code'
error_code_path = root_path.joinpath("error_code")
i18n_folder_path = root_path.joinpath("i18n")
zh_file_path = i18n_folder_path.joinpath("zh.json")
en_file_path = i18n_folder_path.joinpath("en.json")
zh_json = {}
en_json = {}


def filter_init_file(x):
    return not x.startswith("__")


def file_to_json(module, code_type):
    base_classes = getattr(module, code_type).__bases__
    for b in base_classes:
        if b.__name__ not in ["Code"]:  # 去除基类
            _array = [s for s in b.__dict__ if not (s.startswith("__") or 'code_level' in s)]
            for _func in _array:
                func_result = getattr(getattr(module, code_type), _func)()
                zh_json[func_result['code']] = func_result['zh']
                en_json[func_result['code']] = func_result['en']

    code_array = [s for s in getattr(module, code_type).__dict__ if not (s.startswith("__") or 'code_level' in s)]

    for func in code_array:
        func_result = getattr(getattr(module, code_type), func)()
        zh_json[func_result['code']] = func_result['zh']
        en_json[func_result['code']] = func_result['en']


# 遍历module中的ErrorCode/SuccessCode/WarningCode/InfoCode所对应的中英文翻译
def generate_code_json():
    base_code_module = importlib.import_module(base_module)
    # 过滤以__开头和Code的module
    base_code_array = [s for s in dir(base_code_module) if not (s.startswith("__") or s == 'Code')]
    for func in base_code_array:
        file_to_json(base_code_module, func)
    has_language_files = filter(filter_init_file, os.listdir(error_code_path))
    for file_name in list(has_language_files):
        module = importlib.import_module(f'{path_module}.{os.path.splitext(file_name)[0]}')
        error_code_array = [s for s in dir(module) if not (s.startswith("__") or 'Base' in s or s == 'Code')]  # 去除base
        for func in error_code_array:
            file_to_json(module, func)


def main():
    try:
        os.mkdir(i18n_folder_path)
        logger.info("i18n文件夹创建成功")
    except FileExistsError:
        pass
    except OSError as error:
        logger.error(f"创建i18n文件夹出错: {error}")

    generate_code_json()

    def write_file(file_path, data):
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            logger.info("生成I18n文件成功")
        except OSError as err:
            logger.error(f"写入I18n文件出错: {err}")

    write_file(zh_file_path, zh_json)
    write_file(en_file_path, en_json)


if __name__ == '__main__':
    main()
