def singleton(class_):
    """
    Декоратор класса для создания паттерна Singleton
    :param class_:
    :return: единственный экземпляр класса
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
