import logging
import time

import yaml

config_file = 'config.yaml'
emailerConfigFile = 'emailerConfig.yaml'

def load_config(config_file):
    try:
        with open(file=config_file, mode='r') as file:
            config = yaml.safe_load(stream=file)
            barracuda_username = config.get('BARRACUDA_USERNAME')
            barracuda_password = config.get('BARRACUDA_PASSWORD')
            barracuda_url = config.get('BARRACUDA_URL')
    except FileNotFoundError:
        logging.error('Config file not found.')
        raise ValueError('Config file not found.')
    if not all([barracuda_username, barracuda_password, barracuda_url]):
        logging.error(msg='One or more environment variables are missing.')
        raise ValueError('One or more environment variables are missing.')
    return config

def check_config_changes(current_config):
    while True:
        # check for changes in the config file
        new_config = load_config(config_file=config_file)
        if new_config != current_config:
            logging.info(msg='Configuration file has been updated')
            current_config = new_config
        time.sleep(10)

def fnEmailerLoadConfig(emailerConfigFile):
    try:
        with open(file=emailerConfigFile, mode='r') as file:
            data = yaml.safe_load(stream=file)
    except FileNotFoundError:
        logging.error(msg='Config file not found.')
        raise

    senderaddress = data.get('FROM_EMAIL_USERNAME')
    senderpassword = data.get('FROM_EMAIL_PASSWORD')
    smtp_server = data.get('SMTP_SERVER')
    port = data.get('SMTP_PORT')

    if not all([senderaddress, senderpassword, smtp_server, port]):
        logging.error(msg='One or more environment variables are missing.')
        raise ValueError('One or more environment variables are missing.')
    return senderaddress, senderpassword, smtp_server, port