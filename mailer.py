import smtplib
import subprocess
import time
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from checkcsv import check_credit_card, obfuscate_cc
from configs_setup import load_emailer_config_file, setup_logger, EMAIL_CONFIG_FILE, MAIN_CSV_FILE

logger = setup_logger('getMailerLogger', "logs/mailer.log")

def func_read_csv_file(running_file):
    existing_data = []
    try:
        with open(MAIN_CSV_FILE, "r", encoding="utf-8", errors="ignore"):
            data_frame = pd.read_csv(MAIN_CSV_FILE, encoding='utf-8')
        data_frame = check_credit_card(data_frame)
        data_frame = data_frame[(data_frame["emailStatus"].astype(str) != "1")]
        # logger.debug("Data read from CSV file:%s%s", data_frame.to_string().encode('utf-8', errors='replace').decode('utf-8'), existing_data)
        existing_data = data_frame.to_dict("records")
    except FileNotFoundError:
        logger.error("CSV file not found: %s", running_file)
    except Exception as err_except:  # pylint: disable=broad-except
        logger.error("Error reading existing data from CSV file: %s", {str(err_except)})
    return existing_data

def update_sent_column(email_list):
    try:
        data_frame = pd.read_csv(MAIN_CSV_FILE)
        for index, row in data_frame.iterrows():
            if row["To"] in email_list:
                data_frame.at[index, "emailStatus"] = "1"
                # logger.debug("Updating CSV file with %s and %s", row, email_list)
        data_frame.to_csv(MAIN_CSV_FILE, index=False, encoding='utf-8', errors='ignore')
    except Exception as err_except:  # pylint: disable=broad-except
        logger.error("Error updating sent column: %s", {str(err_except)})

def func_send_emails(server, senderaddress, email_data, content):
    current_time = datetime.now().time()
    unique_emails = {data["To"] for data in email_data}
    # logger.info("Sending email to unique: %s", unique_emails)
    for recipient_email in unique_emails:
        # logger.info("Current recipient_email: %s", recipient_email)
        if recipient_email in content:
            # logger.info("Preparing to send email to: %s", recipient_email)
            try:
                for timer in range(20, 0, -10):
                    logger.info("Next email will be sent to %s with subject %s in %s seconds.", recipient_email, content[recipient_email]["Subject"], timer)
                    time.sleep(10)
                email_content = content[recipient_email]
                email_content["Subject"] = obfuscate_cc(email_content["Subject"])
                # response = server.sendmail(f"Zen Alerts <{senderaddress}>", recipient_email, email_content.as_string(),)
                server.sendmail(f"Zen Alerts <{senderaddress}>", recipient_email, email_content.as_string(),)
                # logger.debug(msg=f"Response from sendmail for {recipient_email}: {response}")
                update_sent_column([recipient_email])
                logger.info("Email sent to %s with subject %s at %s", recipient_email, email_content["Subject"], current_time)
            except smtplib.SMTPException as e_smtp:
                logger.error("Failed to send email to %s: %s", recipient_email, e_smtp)
                logger.error(traceback.format_exc())

def func_create_email_server(smtp_server, port, senderaddress, senderpassword):
    try:
        logger.info("Connecting to SMTP server %s:%s with username %s, local_hostname='localhost'", smtp_server, port, senderaddress)
        server = smtplib.SMTP(smtp_server, port, local_hostname='localhost')
        server.starttls()
        server.login(senderaddress, senderpassword)
        return server
    except smtplib.SMTPAuthenticationError:
        raise
    except smtplib.SMTPException as e_smtp:
        logger.error("SMTP Exception occurred: %s", {str(e_smtp)})
    except ConnectionError as e_conerr:
        logger.error("Connection Error occurred: %s", {str(e_conerr)})
    except Exception as err_except:  # pylint: disable=broad-except
        logger.error("Unknown error occurred: %s,", {str(err_except)})

def func_create_email_data(email_data):
    # sourcery skip: merge-assign-and-aug-assign
    var_created_email_list = []
    unique_emails = {email["To"] for email in email_data}
    try:
        for recipient_email in unique_emails:
            msg = MIMEMultipart("alternative")
            recipient_name = recipient_email.split("@")[0].capitalize()
            email_subject = f"Quarantined Emails[{datetime.now().strftime('%d/%m/%Y %H:%M')}] | Subject: "
            body = """<p style="color: blue; font-size: 10px; font-family: 'Open Sans', Arial, sans-serif; font-style: italic;">Inbox is not monitored. Please do not reply back.</p>"""
            body += """<p style="font-size: 12px; font-family: 'Open Sans', Arial, sans-serif;">Hi """
            body += f"{recipient_name},"
            body += """<br></p>"""
            body += """<p style="font-size: 12px; font-family: 'Open Sans', Arial, sans-serif;">This automated message is to notify that there are quarantined emails within the Barracuda system linked to  """
            body += f"{recipient_email}."
            body += """</p>"""
            body += """<p style="font-size: 12px; font-family: 'Open Sans', Arial, sans-serif;">If you need to have emails removed from quarantine, please contact your Team Leader first - they're your first point of contact. If they're unable to assist, feel free to reach out to <a href="mailto:ian@zenithpayments.com.au">Ian Menethil</a> or the <a href="mailto:support@foit.com.au">FOIT Help Desk</a>.</p>"""
            body += """<p style="color: red; font-size: 10px; font-family: 'Open Sans', Arial, sans-serif; font-style: italic; text-decoration: underline; font-weight: bold;">Please note that only false positive emails will be released.</p>"""
            body += """<table border='1' cellpadding='5' style='font-size: 10px; font-family: \'Open Sans\', Arial, sans-serif;'>"""
            body += """<tr><th style='background-color:#f2f2f2;color:#696969;'>MessageID</th><th style='background-color:#f2f2f2;color:#696969;'>From</th><th style='background-color:#f2f2f2;color:#696969;'>To</th><th style='background-color:#f2f2f2;color:#696969;'>Subject</th><th style='background-color:#f2f2f2;color:#696969;'>Date</th><th style='background-color:#f2f2f2;color:#696969;'>Size</th><th style='background-color:#f2f2f2;color:#696969;'>Status</th><th style='background-color:#f2f2f2;color:#696969;'>Reason</th></tr>"""
            for email in [e for e in email_data if e["To"] == recipient_email]:
                var_message_id = email["Message ID"]
                from_email = email["From"]
                to_email = email["To"]
                subject_email = email["Subject"]
                date_email = email["Date"]
                size_email = email["Size"]
                action_email = email["Action"]
                reason_email = email["Reason"]
                body += f"<tr><td>{var_message_id}</td><td>{from_email}</td><td>{to_email}</td><td>{subject_email}</td><td>{date_email}</td><td>{size_email}</td><td>{action_email}</td><td>{reason_email}</td></tr>"
            body += """</table><br>"""
            body += """<p style="color: blue; font-size: 10px; font-family: 'Open Sans', Arial, sans-serif; font-style: italic;">Inbox is not monitored. Please do not reply back.</p>"""
            body += """<p style="color: blue; font-size: 8px; font-family: 'Open Sans', Arial, sans-serif; font-style: italic;">This is an automated email. For app-related technical issues, contact <a href="mailto:ian@zenithpayments.com.au">Ian Menethil</a>.</p>"""
            body_plain = f"Hi {recipient_name},\n\n"
            body_plain += "This automated message is to notify that there are quarantined emails within the Barracuda system linked to "
            body_plain += f"{recipient_email}.\n\n"
            body_plain += "If you need to have emails removed from quarantine, please contact your Team Leader first - they're your first point of contact."
            body_plain += "If they're unable to assist, feel free to reach out to Ian Menethil or the FOIT Help Desk.\n\n"
            body_plain += ("Please note that only false positive emails will be released.\n\n")
            for email in [e for e in email_data if e["To"] == recipient_email]:
                var_message_id = email["Message ID"]
                from_email = email["From"]
                to_email = email["To"]
                subject_email = email["Subject"]
                date_email = email["Date"]
                size_email = email["Size"]
                action_email = email["Action"]
                reason_email = email["Reason"]
                body_plain += f"MessageID: {var_message_id}, From: {from_email}, To: {to_email}, Subject: {subject_email}, Date: {date_email}, Size: {size_email}, Action: {action_email}, Reason: {reason_email}\n"
            body_plain += "\nInbox is not monitored. Please do not reply back.\n"
            body_plain += "This is an automated email. For app-related technical issues, contact Ian Menethil.\n"
            all_subjects = " | ".join([email["Subject"]for email in [e for e in email_data if e["To"] == recipient_email]])
            msg["Subject"] = email_subject + all_subjects
            msg["To"] = recipient_email
            part1 = MIMEText(body_plain, "plain", "utf-8")
            msg.attach(part1)
            part2 = MIMEText(body, "html", "utf-8")
            msg.attach(part2)
            logger.info("Created email for %s with subject %s", recipient_email, msg['Subject'])
            var_created_email_list.append(msg)
            # logger.debug(msg)
        # for msg in var_created_email_list:
        #     logger.debug("Email created for: %s", msg["To"])
        return dict(zip(unique_emails, var_created_email_list))
    except Exception as err_except:  # pylint: disable=broad-except
        logger.error("Error: %s", {err_except})

def main(interactive=False, once=False):
    config = load_emailer_config_file(EMAIL_CONFIG_FILE)
    # logger.info(msg="Config loaded.")
    default_wait_time = 1200
    if interactive:
        logger.info("Mailer activated in: Interactive mode")
        wait_time = input("How often do you want to send new emails? Press Enter to use default (20) or enter a number in minutes:")
        logger.info("User entered: %s", wait_time)
        wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    else:
        logger.info("Mailer activated in: Not in interactive mode")
        wait_time = default_wait_time

    def core_actions():
        subprocess.check_call(["python", "checkcsv.py"])
        print('After calling checkcsv.py in the loop')
        existing_data = func_read_csv_file(MAIN_CSV_FILE)
        do_not_send_list = ['']
        existing_data = [data for data in existing_data if data["To"] not in do_not_send_list and (data["emailStatus"] != "1")]
        # logger.debug("Emails to be sent: %s", [data['To'] for data in existing_data])
        if existing_data:
            server = func_create_email_server(config[2], config[3], config[0], config[1])
            email_content = func_create_email_data(existing_data)
            # logger.debug("Logging email content: %s, existing data: %s", email_content, existing_data)
            func_send_emails(server, config[0], existing_data, email_content)
    if once:  # If 'once' is True, execute core actions only once.
        core_actions()
        return
    while True:
        try:
            core_actions()
            total_seconds_left = wait_time
            while total_seconds_left > 0:
                logger.info("Next run scheduled in %s minutes", total_seconds_left / 60)
                time.sleep(60)
                total_seconds_left -= 60
        except Exception as err_except:  # pylint: disable=broad-except
            logger.error("Error: %s", err_except)
            traceback.print_exc()

if __name__ == "__main__":
    main()
