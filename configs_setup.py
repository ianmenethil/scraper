import logging
import time

import yaml

CONFIG_FILE = 'config.yaml'
EMAIL_CONFIG_FILE = 'emailerConfig.yaml'
ERROR_FNF = 'Config file not found.'
ERROR_VARS_MISSING = 'One or more environment variables are missing.'

def load_config(config_file):
    try:
        with open(file=config_file, mode='r', encoding="utf-8") as file:
            config = yaml.safe_load(stream=file)
            barracuda_username = config.get('BARRACUDA_USERNAME')
            barracuda_password = config.get('BARRACUDA_PASSWORD')
            barracuda_url = config.get('BARRACUDA_URL')
    except FileNotFoundError as exc:
        logging.error(ERROR_FNF)
        raise ValueError(ERROR_FNF) from exc
    if not all([barracuda_username, barracuda_password, barracuda_url]):
        logging.error(msg=ERROR_VARS_MISSING)
        raise ValueError(ERROR_VARS_MISSING)
    return config

def check_config_changes(current_config):
    while True:
        # check for changes in the config file
        new_config = load_config(config_file=CONFIG_FILE)
        if new_config != current_config:
            logging.info(msg='Configuration file has been updated')
            current_config = new_config
        time.sleep(10)

def load_emailer_config_file(email_config_file):
    try:
        with open(file=email_config_file, mode='r', encoding="utf-8") as file:
            data = yaml.safe_load(stream=file)
    except FileNotFoundError:
        logging.error(msg=ERROR_FNF)
        raise

    senderaddress = data.get('FROM_EMAIL_USERNAME')
    senderpassword = data.get('FROM_EMAIL_PASSWORD')
    smtp_server = data.get('SMTP_SERVER')
    port = data.get('SMTP_PORT')

    if not all([senderaddress, senderpassword, smtp_server, port]):
        logging.error(msg=ERROR_VARS_MISSING)
        raise ValueError(ERROR_VARS_MISSING)
    return senderaddress, senderpassword, smtp_server, port
