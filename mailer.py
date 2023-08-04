import logging
# import os
import smtplib
import subprocess
import time
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from checkcsv import fnCheckCC, obfuscate_cc
from config import fnEmailerLoadConfig

config_file = "emailerConfig.yaml"
running_file = "data\\main.csv"

logging.basicConfig(filename="logs\\senderlogs.log",level=logging.DEBUG,encoding="utf-8",format="%(asctime)s - %(levelname)s - %(message)s",datefmt="%Y-%m-%d %H:%M:%S",filemode="a",)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.max_colwidth", 100)

def func_read_csv_file(running_file):
    debug_message = "Reading with unicode_escape from mailer.py readcsvfile"
    print(debug_message)
    existing_data = []
    try:
        with open(running_file, "r", encoding="utf-8", errors="ignore") as f:
            print("Reading with unicode_escape from mailer.py readcsvfile")
            df = pd.read_csv(running_file, encoding='unicode_escape')
        df = fnCheckCC(df)
        df = df[(df["emailStatus"].astype(str) != "1")]
        logging.info(
            f"Data read from CSV file: {df} existing_data : {existing_data}")
        logging.info(f"Data read from CSV file: {df.to_string().encode('utf-8', errors='replace').decode('utf-8')} existing_data : {existing_data}")
        existing_data = df.to_dict("records")
    except FileNotFoundError:
        logging.warning(f"CSV file not found: {running_file}")
    except Exception as e:
        logging.error(f"Error reading existing data from CSV file: {str(e)}")
    return existing_data

def func_update_sent_column(email_data, email_list):
    try:
        df = pd.read_csv(running_file)
        for index, row in df.iterrows():
            if row["To"] in email_list:
                df.at[index, "emailStatus"] = "1"
                logging.info(f"Updating CSV file with {row} and {email_list}")
        df.to_csv(running_file, index=False, encoding='utf-8', errors='ignore')
    except Exception as e:
        logging.error(f"Error updating sent column: {str(e)}")

def func_send_emails(server, senderaddress, email_data, content):
    unique_emails = set([data["To"] for data in email_data])
    logging.info(f"func_send_emails(server, Sending email to unique{unique_emails}")
    for recipient_email in unique_emails:
        logging.info(f"Current recipient_email: {recipient_email}")
        if recipient_email in content:
            logging.info(f"Preparing to send email to: {recipient_email}")
            try:
                email_content = content[recipient_email]
                email_content["Subject"] = obfuscate_cc(email_content["Subject"])
                response = server.sendmail(f"Zen Alerts <{senderaddress}>",recipient_email,email_content.as_string(),)
                logging.info(msg=f"Response from sendmail for {recipient_email}: {response}")
                func_update_sent_column(email_data, [recipient_email])
                for t in range(20, 0, -1):
                    print(f"Next email will be sent in {t} seconds")
                    time.sleep(1)
                print("Email sent!")
            except Exception as e:
                logging.error(f"Failed to send email to {recipient_email}: {e}")
                logging.error(traceback.format_exc())

def func_create_email_server(smtp_server, port, senderaddress, senderpassword):
    try:
        logging.info(f"Connecting to SMTP server {smtp_server}:{port} with username {senderaddress}")
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(senderaddress, senderpassword)
        logging.info("Logged in to SMTP server.")
        return server
    except smtplib.SMTPAuthenticationError:
        raise
    except Exception as e:
        logging.error(f"Error connecting to SMTP server: {str(e)}")

def func_create_email_data(email_data):
    logging.info("func_create_email_data email_data")
    var_created_email_list = []
    unique_emails = set([email["To"] for email in email_data])
    try:
        for recipient_email in unique_emails:
            msg = MIMEMultipart("alternative")
            recipient_name = recipient_email.split("@")[0].capitalize()
            email_subject = f"Quarantined Emails[{datetime.today().strftime('%d/%m/%Y %H:%M')}] | Subject: "
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
            part1 = MIMEText(body_plain, "plain")
            msg.attach(part1)
            part2 = MIMEText(body, "html")
            msg.attach(part2)
            logging.info(f"Created email for {recipient_email} with subject {msg['Subject']}")
            var_created_email_list.append(msg)
            logging.debug(msg)
        for msg in var_created_email_list:
            logging.info("var_created_email_list: %s", msg["To"])
        return {email: msg for email, msg in zip(unique_emails, var_created_email_list)}
    except Exception as e:
        logging.error(f"Error: {e}")

def main():
    print('Before calling checkcsv.py')
    subprocess.check_call(["python", "checkcsv.py"])
    print('After calling checkcsv.py')
    config = fnEmailerLoadConfig(config_file)
    logging.info(msg="Config loaded.")
    default_wait_time = 1200
    wait_time = input("How often do you want to send new emails? Press Enter to use default (20) or enter a number in minutes:")
    logging.info(f"User entered: {wait_time}")
    wait_time = default_wait_time if wait_time == "" else int(wait_time) * 60
    while True:
        try:
            total_seconds_left = wait_time
            while total_seconds_left > 0:
                subprocess.check_call(["python", "checkcsv.py"])
                print('After calling checkcsv.py in the loop')
                existing_data = func_read_csv_file(running_file)
                # do_not_send_list = ['kim@zenithpayments.com.au']
                do_not_send_list = ['']
                existing_data = [
                    data
                    for data in existing_data
                    if data["To"] not in do_not_send_list and (data["emailStatus"] != "1")]

                logging.info(f"Emails to be sent: {[data['To'] for data in existing_data]}")
                server = func_create_email_server(config[2], config[3], config[0], config[1])
                email_content = func_create_email_data(existing_data)
                logging.info("Logging email content", email_content)
                logging.info("Email data: {existing_data}")
                func_send_emails(server, config[0], existing_data, email_content)

                logging.info(f"Sleep time | Total left: {total_seconds_left} seconds.")
                print(f"Next run scheduled in {total_seconds_left / 60} minutes")
                time.sleep(10)
                total_seconds_left -= 10
        except Exception as e:
            logging.error(f"Error: {e}")
            traceback.print_exc()
if __name__ == "__main__":
    main()
