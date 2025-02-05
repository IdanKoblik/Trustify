from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional
import logging
import os 

@dataclass
class Config:
    public_token: str
    private_token: str
    pgsql_connection: str

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None
    
    def __new__(cls, env_vars: Optional[list[str]] = None, config_file: Optional[str] = "config.json"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.env_vars = env_vars if env_vars else [
                "PUBLIC_AUTH_SERVER",
                "PRIVATE_AUTH_SERVER",
                "PGSQL_CONNECTION"
            ]
            cls._instance.config_file = config_file
            cls._instance.config = None
            
        return cls._instance
    
    def load_from_env(self) -> bool:
        env_config = {}
        for var in self.env_vars:
            value = os.environ.get(var)
            if value:
                env_config[var] = value
            else:
                logger.debug(f"Environment variable '{var}' not found.")
        
        return env_config if env_config else None

    def load_from_json(self) -> Optional[Config]:
        try:
            with open(self.config_file, "r") as file:
                data = json.load(file)
                config = Config(
                    public_token=data.get("public", ""),
                    private_token=data.get("private", ""),
                    pgsql_connection=data.get("pgsql_connection", "")
                )
                
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file '{self.config_file}' not found.")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON format in '{self.config_file}'.")
        except Exception as e:
            logger.error(f"An error occurred while reading the config file: {e}")
        return None

    def merge_config_and_env(self, config_data: Config, env_data: dict) -> Config:
        if "PUBLIC_AUTH_SERVER" in env_data:
            logger.debug("Overriding public_token with value from environment.")
            config_data.public_token = env_data["PUBLIC_AUTH_SERVER"]
        if "PRIVATE_AUTH_SERVER" in env_data:
            logger.debug("Overriding private_token with value from environment.")
            config_data.private_token = env_data["PRIVATE_AUTH_SERVER"]
        if "PGSQL_CONNECTION" in env_data:
            logger.debug("Overriding pgsql_connection with value from environment.")
            config_data.pgsql_connection = env_data["PGSQL_CONNECTION"]
        return config_data

    def load_config(self) -> bool:
        env_config = self.load_from_env()
        config_data = self.load_from_json()

        if env_config and config_data:
            logger.debug("Merging configuration from file and environment.")
            self.config = self.merge_config_and_env(config_data, env_config)
        elif env_config:
            logger.debug("Only environment configuration found.")
            self.config = Config(
                public_token=env_config.get("PUBLIC_AUTH_SERVER", ""),
                private_token=env_config.get("PRIVATE_AUTH_SERVER", ""),
                pgsql_connection=env_config.get("PGSQL_CONNECTION", "")
            )
        elif config_data:
            logger.debug("Only configuration file found.")
            self.config = config_data
        else:
            logger.error("No configuration available from either environment or file.")
            return False
        
        return True

    def get_config(self) -> Optional[Config]:
        return self.config