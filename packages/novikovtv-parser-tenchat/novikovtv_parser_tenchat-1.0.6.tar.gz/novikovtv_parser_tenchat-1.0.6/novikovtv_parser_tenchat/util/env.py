import os

from dotenv import load_dotenv, find_dotenv

from novikovtv_parser_tenchat.util.singleton import singleton


@singleton
class ENV(object):
    """
    Класс представляющий переменные окружения.
    Является Singleton
    """

    def __init__(self):
        isLoaded: bool = load_dotenv(dotenv_path=find_dotenv())
        if not isLoaded:
            raise Exception("Env variables are not loaded")

        self.__env = {}
        with open(find_dotenv(), 'r', encoding='utf-8') as envFile:
            for line in envFile.readlines():
                key = line.split("=")[0]
                self.__env[key] = os.getenv(key)

    @property
    def env(self) -> dict:
        return self.__env
