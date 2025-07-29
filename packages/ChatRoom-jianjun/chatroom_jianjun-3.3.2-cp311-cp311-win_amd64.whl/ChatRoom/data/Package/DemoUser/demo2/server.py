# -*- coding: utf-8 -*-
# AucoCython No Compile
# 本包服务端用户名称为 DemoUser
import os
import time
import queue
from ChatRoom.package import BaseServer
import DemoUser.demo2 as SelfPackage

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
        return  a + b

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

    """ MapReduce 相关函数 """
    def map_result(self, run_id, result):
        """ 接收 Map 函数的计算结果的回调函数 """
        self.map_result_queue.put((run_id, result))

    def mapreduce(self):
        """ MapReduce 示例 """
        # NOTE 一个简易的 MapReduce 示例

        # 生成任务队列, 理论运行时间 3s
        task_dict = {}
        for run_id in range(30):
            task_dict[run_id] = [1, 2]

        # 1.不使用 MapReduce 的方式
        def no_mapreduce():
            def map_func(run_id, a, b):
                """ 测试的map函数 """
                # 假设该函数需要耗时 0.1s
                time.sleep(0.1)
                result = a + b
                return run_id, result

            start_time = time.time()
            # Map
            map_result_queue = queue.Queue()
            for run_id, task_args in task_dict.items():
                r_run_id, result = map_func(run_id, *task_args)
                map_result_queue.put((r_run_id, result))

            # Reduce
            all_task_run_id_set = set(task_dict)
            all_result = 0
            while all_task_run_id_set:
                # 如果任务未结束
                run_id, result = map_result_queue.get()
                all_result += result
                all_task_run_id_set.remove(run_id)

            print("最终结果: {0}".format(all_result))
            print("直接计算耗时: {0}".format(time.time() - start_time))

        no_mapreduce()

        # 2.使用分布式 MapReduce
        start_time = time.time()
        self.map_result_queue = queue.Queue()
        # 获取使用该包的客户的用户名称
        client_package_info = self.get_client_package_info()
        """
        # 可以获取其他载入了本包的客户端用户包信息
        {'Bar': {'Foo_demo2': {'SERVER': 'Foo', 'ENABLE': True, 'AUTO_UPDATE': True, 'THERMAL_RENEWAL': True, 'NAME': 'demo2', 'INTRODUCTION': 'demo introduction', 'VERSION': 'v1.0.0', 'SCHEDULED_INSTALL_VERSION': [], 'HISTORY_VERSION': [], 'AUTHOR': 'Demo User', 'AUTHOR_EMAIL': 'xxx@gmail.com', 'URL': 'https://xxx.xxx.com', 'REQUIRES': ['pandas>=1.5.0', 'requests==2.28.1'], 'PLATFORM': 'Windows', 'PYTHON_VERSION': '>=3.8.0', 'SAFE_PATH_LIST': ['$PAC/data', 'package_test_path']}}, 'Too': {'Foo_demo2': {'SERVER': 'Foo', 'ENABLE': True, 'AUTO_UPDATE': True, 'THERMAL_RENEWAL': True, 'NAME': 'demo2', 'INTRODUCTION': 'demo introduction', 'VERSION': 'v1.0.0', 'SCHEDULED_INSTALL_VERSION': [], 'HISTORY_VERSION': [], 'AUTHOR': 'Demo User', 'AUTHOR_EMAIL': 'xxx@gmail.com', 'URL': 'https://xxx.xxx.com', 'REQUIRES': ['pandas>=1.5.0', 'requests==2.28.1'], 'PLATFORM': 'Windows', 'PYTHON_VERSION': '>=3.8.0', 'SAFE_PATH_LIST': ['$PAC/data', 'package_test_path']}}}
        """
        print("客户端数量: {0} 用户列表: {1}".format(len(client_package_info), client_package_info.keys()))

        if not client_package_info:
            print("所有客户都都未在线!")
            return

        # 获取用户名称生成器
        def get_user_name():
            # 这里也可以加上判断对方载入的包的信息, 比如包的版本等来过滤用户
            while True:
                for user_name in client_package_info:
                    yield user_name
        gen_user_name = get_user_name()

        # Map
        for run_id, task_args in task_dict.items():
            # 向客户端用户平均分配任务, 也可以更复杂的实现查看客户都任务信息动态分配任务
            self.send_to_user(next(gen_user_name), "map_func", run_id, *task_args)
            # 根据需求可以使用 self.get_to_user 函数调用 get 类型的回调函数, 只是 get 类型会进行阻塞, 所以上面使用了 self.send_to_user

        # Reduce
        all_task_run_id_set = set(task_dict)
        all_result = 0
        while all_task_run_id_set:
            # 如果任务未结束
            run_id, result = self.map_result_queue.get()
            all_result += result
            all_task_run_id_set.remove(run_id)

        print("最终结果: {0}".format(all_result))
        print("MapReduce耗时: {0}".format(time.time() - start_time))

    """ 在构造函数中注册回调函数等操作 """
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        # 服务端分享变量示例
        # (这里加了前缀包名: DemoUser_demo2, 为了不和其他的分享变量重名)
        # DemoUser表示开发着如果包的作者, demo2为包名, 这么加是为了可能与 Too 开发的 demo2 共享的变量不重名
        self.share.DemoUser_demo2_hello_server = "Hello ChatRoom! i'm Server!"

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

        self.register_send_event_callback_func("map_result", self.map_result)