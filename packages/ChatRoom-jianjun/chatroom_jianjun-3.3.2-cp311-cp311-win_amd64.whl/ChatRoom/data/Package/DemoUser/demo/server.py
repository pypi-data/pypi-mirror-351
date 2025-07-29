# -*- coding: utf-8 -*-
# AucoCython No Compile
import os

from ChatRoom.package import BaseServer
import DemoUser.demo as SelfPackage

# 本包服务端用户名称为 DemoUser
try:
    #  从本包路径中导入自定义动态链接库
    from DemoUser.demo.Lib.ext_lib import plus
except (ImportError, ModuleNotFoundError):
    # 我的动态链接库为 ext_lib.cp310-win_amd64.pyd, 只支持 cpython 3.10
    # 这里只是例子, 如果你在其他环境中使用自己的动态链接库就像上面的路径这样导入就好
    # 下面是 plus 函数的源代码
    print("使用源代码!")
    def plus(a, b):
        print("i'm dll function, im runing..")
        return a + b

# 获取本包路径
# 在不同的设备上运行服务端或客户端, 都可以使用这个 SelfPackage.__path__[0] 都可以获取到当前运行环境的包的路径, 来使用包的一些文件
PAC_PATH = SelfPackage.__path__[0]
# ChatRoom v3.3.2 后可以使用 self.path 替代 PAC_PATH

# 演示文件路径
DATA_PATH = os.path.join(PAC_PATH, "data")
INFO_PATH = os.path.join(DATA_PATH, "info.txt")
CONFIG_PATH = os.path.join(DATA_PATH, "config.json")
DOWALOAD_PATH = os.path.join(DATA_PATH, "TestDownloadFile")

class Server(BaseServer):
    """ 服务端代码 """

    """ 自定义工作函数 """
    def fun1(self):
        """
        文档:
            send 示例 1
        """
        print("I'm fun1!")

    def fun2(self, args):
        """
        文档:
            send 示例 2
        参数:
            args: any
                任意数据
        """
        print("I'm fun2:, i recv: {0}".format(args))

    def fun3(self):
        """
        文档:
            get 示例 1
        返回:
            服务端返回 True
        """
        print("I'm fun3!")
        return True

    def fun4(self, a, b):
        """
        文档:
            get 示例 2
        参数:
            a: int or float
                数字a
            b: int or float
                数字b
        返回:
            plus(a, b)
        """
        print("I'm fun4:, i recv: {0} {1}".format(a, b))
        # 调用导入的本包动态链接库函数示例
        return plus(a, b)

    def fun5(self, get_file):
        """
        文档:
            使用包内文件示例
        参数:
            get_file: str
                文件名 "info" or "config"
        """
        print("get_file: {0}".format(get_file))
        if get_file == "info":
            file_path = INFO_PATH
        elif get_file == "config":
            file_path = CONFIG_PATH

        with open(file_path, "r", encoding="utf-8") as fr:
            file_info = fr.read()

        return file_info

    def fun6(self):
        """
        文档:
            获取请求的用户实例和名称示例
        返回:
            获取请求的用户名称
        """
        current_user = self.current_user
        print("current_user: ", current_user)
        current_user_name = self.current_user_name
        print("current_user_name: ", current_user_name)

        return current_user_name

    def fun7(self, file_name):
        """
        文档:
            下载文件(传输文件示例)
        参数:
            file_name: str
                文件名 "TestDownloadFile"
        """
        if file_name == "TestDownloadFile":
            # 收到客户端发送的下载请求, 主动向客户端发送需要的文件
            send_file_process = self.send_file(DOWALOAD_PATH, os.path.join("package_test_path", "TestDownloadFile"), show=True, wait=True)
            # 如果是需要从客户端上下载文件可以使用 self.recv_file 函数

            if send_file_process.statu == "success":
                print("文件发送成功!")
            else:
                print("文件发送失败!")

    def fun8(self):
        """
        文档:
            读取请求 User 分享变量 和 状态 示例
        """
        share = self.current_user.share
        status = self.current_user.status

        print("share: ", share)
        print("status: ", status)

    def fun9(self):
        """
        文档:
            发送日志 示例, 日志id为 log.py 中配置的日志id
        """
        self.log_id("00001")
        self.log_id("00003")
        # 也可以使用 log 函数自定义日志类型和日志文本
        self.log("00001", "WAR", "DEMO_00001_WAR_info")

    def fun10(self):
        """
        文档:
            按照 ChatRoom 的消息格式显示自定义消息
        文档:
            显示标准格式的信息

        self.show_info
        参数:
            title : str
                信息标题, 不超过25个字符宽
            info : str
                信息文本
            style : str
                显示的颜色央视
                    None        : 无颜色 (default)
                    red(r)      : 红色
                    green(g)    : 绿色
                    orange(o)   : 橙色
                    yellow(y)   : 黄色
                    purple(p)   : 紫色
                    blue(b)     : 蓝色
        """
        title = "TITLE"
        info = "TEST 123 ABC"
        self.show_info(title, info)
        self.show_info(title, info, style="r")
        self.show_info(title, info, style="g")
        self.show_info(title, info, style="o")
        self.show_info(title, info, style="y")
        self.show_info(title, info, style="p")
        self.show_info(title, info, style="b")

    """ 在构造函数中注册回调函数等操作 """
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        # 服务端分享变量示例
        # (这里加了前缀包名: DemoUser_demo, 为了不和其他的分享变量重名)
        # DemoUser表示开发着如果包的作者, demo为包名, 这么加是为了可能与 Too 开发的 demo 共享的变量不重名
        self.share.DemoUser_demo_hello_server = "Hello ChatRoom! i'm Server!"

        # 按需注册回调函数
        self.register_send_event_callback_func("fun1", self.fun1)
        self.register_send_event_callback_func("fun2", self.fun2)
        self.register_get_event_callback_func("fun3", self.fun3)
        self.register_get_event_callback_func("fun4", self.fun4)
        self.register_get_event_callback_func("fun5", self.fun5)
        self.register_get_event_callback_func("fun6", self.fun6)
        self.register_send_event_callback_func("fun7", self.fun7)
        self.register_send_event_callback_func("fun8", self.fun8)
        self.register_send_event_callback_func("fun9", self.fun9)
