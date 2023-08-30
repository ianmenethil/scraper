import logging
import yaml

MAIN_CONFIG_FILE = 'config.yaml'
EMAIL_CONFIG_FILE = 'emailerConfig.yaml'
MAIN_CSV_FILE = './data/main.csv'
DATA_DIRECTORY = './data/'
FILE_EXTENSION = '.csv'

ERROR_FNF = 'Config file not found.'
ERROR_VARS_MISSING = 'One or more environment variables are missing.'

def setup_logger(name, log_file, level=logging.INFO):
    # sourcery skip: extract-duplicate-method
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # File handler
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(level)
    file_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console.setFormatter(console_format)
    logger.addHandler(console)
    return logger

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
