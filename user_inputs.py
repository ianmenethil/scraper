def get_choice():
    # valid_choice = ['1', '2']
    # while True:
    #     userinput_valid_choice = input("Enter '1' for manual mode or '2' for automatic mode: ")
    #     logging.info("User entered: %s", {userinput_valid_choice})
    #     if userinput_valid_choice in valid_choice:
    #         return userinput_valid_choice
    #     else:
    #         logging.info("Invalid input. Please enter one of the following: %s", {valid_choice})
    userinput_valid_choice = '2'
    return userinput_valid_choice

def auto_flow():
    default_wait_time = 1200  # 20 minutes
    wait_time = input(
                        """
                        The default timer for emails is 20 minutes.
                        Press enter to use the default timer or enter a new timer in minutes:
                        """)
    print("User entered: %s", {wait_time})
    wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    choice = '2'
    # return should_exit, wait_time, choice
    return wait_time, choice
