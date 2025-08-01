import logging
import sys
import yaml
from pathlib import Path
from ..core.config import settings

def configure_logging():
    """Configure application logging"""
    log_config_path = Path(__file__).parent.parent.parent / "config" / "logging.yaml"
    try:
        with open(log_config_path) as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    except Exception as e:
        # Fallback basic config if YAML loading fails
        logging.basicConfig(
            level=logging.INFO if settings.APP_ENV == "production" else logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.getLogger().warning(f"Failed to load logging config: {str(e)}. Using basic config.")