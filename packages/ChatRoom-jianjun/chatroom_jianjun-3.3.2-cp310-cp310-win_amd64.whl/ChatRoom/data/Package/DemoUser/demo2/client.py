# -*- coding: utf-8 -*-
# AucoCython No Compile
# 本包客户端用户名称为 DemoUser
import time
from ChatRoom.package import BaseClient
import DemoUser.demo2 as SelfPackage
from DemoUser.demo2.ext_lib import plus

# 获取本包路径
# 在不同的设备上运行服务端或客户端, 都可以使用这个 SelfPackage.__path__[0] 都可以获取到当前运行环境的包的路径, 来使用包的一些文件
PAC_PATH = SelfPackage.__path__[0]
# ChatRoom v3.3.2 后可以使用 self.path 替代 PAC_PATH

class Client(BaseClient):

    """ 和服务端对应的函数 """
    def fun1(self):
        """
        文档:
            调用服务端 fun1
        """
        self.send_to_server("fun1")

    def fun2(self, args):
        """
        文档:
            调用服务端 fun2
        参数:
            args: any
                任意数据
        """
        self.send_to_server("fun2", args)

    def fun3(self):
        """
        文档:
            调用服务端 fun3
        返回:
            服务端返回 True
        """
        return self.get_to_server("fun3")

    def fun4(self, a, b):
        """
        文档:
            调用服务端 fun4
            服务端返回 a + b 的值
            本机计算 a + b 的值
        参数:
            a: int or float
                数字a
            b: int or float
                数字b
        """
        server_result = self.get_to_server("fun4", a, b)
        # 客户端调用本包py文件等
        client_result = plus(a, b)

        print("server_result: ", server_result)
        print("client_result: ", client_result)

    def fun5(self, get_file):
        """
        文档:
            调用服务端 fun5
        参数:
            get_file: str
                文件名 "info" or "config"
        """
        return self.get_to_server("fun5", get_file)

    def fun6(self):
        """
        文档:
            调用服务端 fun6
        返回:
            获取请求的用户名称, 就是返回本 User 的名称
        """
        return self.get_to_server("fun6")

    def fun7(self, file_name):
        """
        文档:
            调用服务端 fun7 下载文件
        参数:
            file_name: str
                文件名 "TestDownloadFile"
        """
        self.send_to_server("fun7", file_name)

    def fun8(self):
        """
        文档:
            调用服务端 fun8
            调用 服务端 读取 客户端 分享的共享变量
        """
        self.send_to_server("fun8")

    def fun9(self):
        """
        文档:
            客户端 读取 服务端 分享的共享变量
        """
        share = self.server_user.share
        status = self.server_user.status

        print("share: ", share)
        print("status: ", status)

    def fun10(self):
        """
        文档:
            调用服务端 fun9
            调用 服务端, 服务端会发送日志
            客户端也发送日志
        """
        self.send_to_server("fun9")
        self.log_id("00002")

    """ MapReduce 相关函数 """
    def map_func(self, run_id, a, b):
        """ 测试的map函数 """
        # 假设该函数需要耗时 0.1s
        time.sleep(0.1)
        result = a + b
        # 把结果发送到服务端, 发送计算的 run_id 和 结果 result
        self.send_to_server("map_result", run_id, result)

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        # 共享自生变量
        # (这里加了前缀包名: DemoUser_demo2, 为了不和其他的分享变量重名)
        # DemoUser表示开发着如果包的作者, demo2为包名, 这么加是为了可能与 Too 开发的 demo2 共享的变量不重名
        self.share.DemoUser_demo2_hello_client = "Hello ChatRoom! i'm Client!"

        # 注册客户端的回调函数, 因为这个函数可能频繁计算, 所以不使用线程启动
        self.register_send_event_callback_func("map_func", self.map_func, thread=False)
