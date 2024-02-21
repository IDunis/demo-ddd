"""
This module contains the configuration class
"""
import logging
from typing import Any, Dict, List, Optional

from nexttrade.configuration.load_config import load_from_files
from nexttrade.constants import Config
from nexttrade.enums import RunMode


logger = logging.getLogger(__name__)


class Configuration:
    """
    Class to read and init the bot configuration
    Reuse this class for the bot, backtesting, hyperopt and every script that required configuration
    """

    def __init__(self, args: Dict[str, Any], runmode: Optional[RunMode] = None) -> None:
        self.args = args
        self.config: Optional[Config] = None
        self.runmode = runmode

    def get_config(self) -> Config:
        """
        Return the config. Use this method to get the bot config
        :return: Dict: Bot config
        """
        if self.config is None:
            self.config = self.load_config()

        self.config.update({
            "dry_run": True,
            "timeframe": "5m",
            "telegram": {
                "enabled": True,
                "token": "6918557089:AAFoQ8-nhmpWR4hhf-_CCXTd2psCqnEglWo",
                "chat_id": "1008005852",
                "notification_settings": {
                    "status": "on",
                    "warning": "on",
                    "startup": "on",
                },
                "reload": False,
            }
        })

        return self.config

    @staticmethod
    def from_files(files: List[str]) -> Dict[str, Any]:
        """
        Iterate through the config files passed in, loading all of them
        and merging their contents.
        Files are loaded in sequence, parameters in later configuration files
        override the same parameter from an earlier file (last definition wins).
        Runs through the whole Configuration initialization, so all expected config entries
        are available to interactive environments.
        :param files: List of file paths
        :return: configuration dictionary
        """
        # Keep this method as staticmethod, so it can be used from interactive environments
        c = Configuration({'config': files}, RunMode.OTHER)
        return c.get_config()

    def load_config(self) -> Dict[str, Any]:
        """
        Extract information for sys.argv and load the bot configuration
        :return: Configuration dictionary
        """
        # Load all configs
        config: Config = load_from_files(self.args.get("config", []))

        return config
