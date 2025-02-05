from flask import Flask
import logging
import logging
from config import ConfigManager
from pgsql import PgSqlManager
from logging_config import configure_logging

logger = logging.getLogger(__name__)
app = Flask(__name__)

app_config = None

def main() -> None:
    configure_logging()
    config_manager = ConfigManager()
    
    if not config_manager.load_config():
        logger.error("Failed to load configuration.")
        return
    
    config = config_manager.get_config()
    if not config:
        logger.error("No configuration loaded.")
        return
    
    pgsql_manager = PgSqlManager()
    if not pgsql_manager.connect(config):
        logger.error("Failed to connect to the database.")
        return
    
    try:
        app.run(debug=True)
    finally:
        pgsql_manager.disconnect()
        
if __name__ == "__main__":
    main()
