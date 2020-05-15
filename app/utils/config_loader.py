import sys
import json
import argparse


def load_config():
    """ Reads command line argument and loads JSON config from given config path

        Returns
        -------
        config (dict) - parsed config JSON

        Raise Exception if file not found or file contains not a valid JSON
    """

    parser = argparse.ArgumentParser()

    # Only one argument is expected
    parser.add_argument("--config_path", required=True, type=str,
                        default=None, help="Path to configuration JSON file")
    args = parser.parse_args()

    # Value of argument
    config_path = args.config_path

    try:
        with open(config_path, "r") as fh:
            return json.load(fh)
    except OSError:
        sys.exit("Configuration file does not exist")
    except json.JSONDecodeError:
        sys.exit("Configuration file is not a valid JSON")
