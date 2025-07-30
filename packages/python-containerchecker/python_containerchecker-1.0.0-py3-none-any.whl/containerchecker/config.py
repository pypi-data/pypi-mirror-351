import logging

import yaml

logger = logging.getLogger("rich")


def read_yaml_file(file_path):
    """Reads a YAML file and returns its contents as a dictionary."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        logger.debug(f"File not found: {file_path}")
    except yaml.YAMLError as exception:
        logger.exception(f"Error parsing YAML file: {file_path} - {exception}")
    except Exception as exception:
        logger.exception(f"An error occurred: {exception}")
