import configparser

CONFIGURATION_PATH = "config.ini"


class SingletonConfiguration:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("Creating Configuration singleton object")
            cls._instance = super(SingletonConfiguration, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(self, config_path):
        self.config_path = config_path

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        return config


global_singleton_config = SingletonConfiguration(CONFIGURATION_PATH)
global_config = global_singleton_config.read_config()
