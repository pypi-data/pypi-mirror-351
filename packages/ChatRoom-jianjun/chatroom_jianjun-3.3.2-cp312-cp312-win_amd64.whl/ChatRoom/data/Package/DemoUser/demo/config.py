# -*- coding: utf-8 -*-
# AucoCython No Compile
class Config():
    """ 包配置 """
    # 启用
    ENABLE = False
    # 自动更新
    AUTO_UPDATE = True
    # 热更新
    THERMAL_RENEWAL = False
    # 包名称
    NAME = "demo"
    # 简介
    INTRODUCTION = "demo introduction"
    # 版本
    VERSION = "v1.0.0"
    # 作者
    AUTHOR = "Demo User"
    # 作者邮箱
    AUTHOR_EMAIL = "xxx@gmail.com"
    # 包官网
    URL = "https://xxx.xxx.com"
    # 依赖包
    REQUIRES = [
        "pandas>=1.5.0",
        "requests==2.28.1",
    ]
    # 依赖环境信息
    REQUIRES_INFO = "The package require pandas and requests."
    # 平台
    PLATFORM = "Windows"
    # Python版本
    PYTHON_VERSION = ">=3.8.0"
    # 安全文件夹列表
    SAFE_PATH_LIST = [
        "$PAC/data",
        "package_test_path",
    ]