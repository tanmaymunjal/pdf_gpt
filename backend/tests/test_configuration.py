import os
import pytest
from backend.configuration import SingletonConfiguration
import configparser

TEST_CONFIGURATION_PATH = "tests/test_config.ini"


def test_singleton_instance():
    # Create two instances of SingletonConfiguration
    singleton_instance1 = SingletonConfiguration(TEST_CONFIGURATION_PATH)
    singleton_instance2 = SingletonConfiguration(TEST_CONFIGURATION_PATH)

    # Assert that both instances refer to the same object
    assert singleton_instance1 is singleton_instance2


def test_read_config():
    # Create an instance of SingletonConfiguration
    singleton_instance = SingletonConfiguration(TEST_CONFIGURATION_PATH)

    # Read the configuration settings
    config = singleton_instance.read_config()

    # Assert that the config object is not None
    assert config is not None

    # Assert that the config object is an instance of ConfigParser
    assert isinstance(config, configparser.ConfigParser)

    # Assert that the config object contains expected configuration values
    assert config.has_option("Application", "TESTING")
    assert config.get("Application", "TESTING") == "1"

    # Assert that the configuration file path is correct
    assert singleton_instance.config_path == TEST_CONFIGURATION_PATH
