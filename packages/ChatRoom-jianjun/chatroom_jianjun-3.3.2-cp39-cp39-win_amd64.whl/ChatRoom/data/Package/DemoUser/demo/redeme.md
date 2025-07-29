# DEMO PACKAGE

    from ChatRoom import User

    user = User(...)

    # load demo package

    client = user.package_manage.get_client("user_name", "demo")

    client.fun1()

    client.fun2("Hello!")

    client.fun3()

    client.fun4(1, 2)

    client.fun5("info")
    client.fun5("config")

    client.fun6()

    client.fun7("TestDownloadFile")

    client.fun8()

    client.fun9()

    client.fun10()