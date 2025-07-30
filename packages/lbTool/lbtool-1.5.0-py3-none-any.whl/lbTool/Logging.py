from datetime import datetime
import logging
from logging import config
import os

import yaml


def get_logger(init_logger="root"):
    """
    获取日志操作对象
    :param init_logger: 默认root，可单独指定
    """
    logger_base = __Logger(init_logger)
    return logger_base.logger


class __Logger:
    def __init__(self, init_logger="root"):
        """
        初始化日志管理类
        :param init_logger: 日志处理器 默认root，可单独指定
        """
        # 配置日志记录 日志级别从低到高 DEBUG->INFO->WARNING->ERROR->CRITICAL
        # 1.基本配置
        # logging.basicConfig(level=logging.DEBUG,  # 设置日志级别为 DEBUG（最低级别）
        #                     filename=f'Log/Logs_{datetime.now().strftime("%Y%m%d")}.log',  # 指定日志文件名
        #                     filemode='a',  # 设置文件模式为追加写入
        #                     format='%(asctime)s - %(levelname)s - %(message)s')
        # 2.加载配置文件
        # logging.config.fileConfig('config/log.conf',
        #                           defaults={
        #                               'Ymd': datetime.now().strftime("%Y%m%d"),
        #                               'dir_name': 'Log'
        #                           },
        #                           disable_existing_loggers=False)
        # 日志输出目录
        dir_name = "Log" + os.sep
        # 日志配置文件路径
        # yml_path = os.path.normpath(os.path.join(os.getcwd(), "config/log.yml"))
        from lbTool import work_dir_path, config_dir_path
        yml_path = os.path.normpath(os.path.join(config_dir_path, "log.yml"))
        # 日志默认等级
        default_level = logging.DEBUG
        # 判定是否日志目录 不存在则创建
        log_dir_path = os.path.join(work_dir_path, dir_name)
        if not os.path.exists(log_dir_path):
            os.mkdir(log_dir_path)
        # 3.使用yml配置文件
        if os.path.exists(yml_path):
            with open(yml_path, "r") as f:
                config_data = yaml.load(f, Loader=yaml.FullLoader)
                # 修改生成文件名，增加日期 形式如app_20231103.log
                for i in (config_data["handlers"].keys()):
                    if 'filename' in config_data['handlers'][i]:
                        log_filename = config_data["handlers"][i]["filename"]
                        base, extension = os.path.splitext(log_filename)
                        log_filename = "{}{}{}{}".format(log_dir_path, base + "_", datetime.now().strftime("%Y%m%d"),
                                                         extension)
                        config_data["handlers"][i]["filename"] = log_filename
            logging.config.dictConfig(config_data)
        else:
            logging.basicConfig(level=default_level)

        # 获取文件输出
        self.logger = logging.getLogger(init_logger)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
