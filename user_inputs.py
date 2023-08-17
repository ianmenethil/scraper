def get_choice():
    userinput_valid_choice = '2'
    return userinput_valid_choice

def auto_flow():
    default_wait_time = 1200  # 20 minutes
    wait_time = input("""
                      The default timer for emails is 20 minutes.
                      Press enter to use the default timer or enter a new timer in minutes:""")
    print(f"User entered: {wait_time}")
    wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    choice = '2'
    return wait_time, choice
