# 导入子模块方法，以便直接从包导入，不用指定模块导入
# .module .为相对导入；也可使用package_name.module_name导入
import os

from .Db import get_orm_con, init_db, generate_pony_entity
# 由于dmPython需要dll支持，暂时无法直接导入使用
# 打包导入dll后，可以使用 2024.11.6
# 导入dm方法打包exe后，如果没有打入dll会导致整个程序无法运行，暂时屏蔽 2025.05.29
# from .DmDb import get_dm_con, init_dm_db, generate_dm_entity
from .Logging import get_logger
from .ConfigManager import ConfigManager

# 程序工作目录
work_dir = os.getcwd()
# 列出目录信息,以便准确识别目录
dir_info = work_dir.split(os.sep)
# 如果工作目录包含以下目录，将只读取其对应的父级目录下的配置目录
filter_dir = ["gui", "study"]
for name in filter_dir:
    if name in dir_info:
        index = work_dir.index(name)
        work_dir = work_dir[:index]

# 其他情况默认当前工作目录
# 当前工作目录
work_dir_path = os.path.normpath(work_dir)
# 工作目录所在的config目录
config_dir_path = os.path.normpath(os.path.join(work_dir, "config"))
