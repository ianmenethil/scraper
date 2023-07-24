import logging

def get_choice():
    valid_choice = ['1', '2']
    while True:
        userinput_valid_choice = input("Enter '1' for manual mode or '2' for automatic mode: ")
        logging.info(f"User entered: {userinput_valid_choice}")
        if userinput_valid_choice in valid_choice:
            return userinput_valid_choice
        else:
            logging.info(f"Invalid input. Please enter one of the following: {valid_choice}")


def inputs_Flow1():
    logging.info('User selected manual mode.')

    valid_inputs = ['1', ' ', '', '2']
    should_exit = False
    wait_time = None
    choice = '1'
    while True:
        user_input = input("Press Enter to rerun immediately or '2' to exit.")
        logging.info(f"User entered: {user_input}")
        if user_input == '2':
            logging.info('Exiting manual mode.')
            should_exit = True
            break
        elif user_input in valid_inputs:
            return should_exit, wait_time, choice
        else:
            logging.info(f"Invalid input. Please enter one of the following: {valid_inputs}")
    return should_exit, wait_time, choice

def inputs_Flow2():
    logging.info('User selected automatic mode.')
    should_exit = False
    default_wait_time = 1200  # 20 minutes
    wait_time = input("How often do you want to check for new emails? Press Enter to use default(20) or enter a number in minutes: ")
    logging.info(f"User entered: {wait_time}")
    wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    choice = '2'
    return should_exit, wait_time, choice