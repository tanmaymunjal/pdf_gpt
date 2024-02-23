import configparser

CONFIGURATION_PATH = "config.ini"


class SingletonConfiguration:
    """
    Singleton class to read and provide access to configuration settings from a file.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of SingletonConfiguration if it does not exist.

        Returns:
            SingletonConfiguration: The instance of SingletonConfiguration.
        """
        if cls._instance is None:
            print("Creating Configuration singleton object")
            cls._instance = super(SingletonConfiguration, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path):
        """
        Initialize the SingletonConfiguration with the path to the configuration file.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config_path = config_path

    def read_config(self):
        """
        Read the configuration settings from the file.

        Returns:
            configparser.ConfigParser: Configuration settings read from the file.
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        return config


global_singleton_config = SingletonConfiguration(CONFIGURATION_PATH)
global_config = global_singleton_config.read_config()
