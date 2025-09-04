import smtplib
from email.message import EmailMessage
import secrets
import mysql.connector
import json

with open('config.json') as f:
    config=json.load(f)
    
mydb=mysql.connector.connect(
    host=config["DB_HOST"],
    user=config["DB_USER"],
    password=config["DB_PASS"],
    database=config["DB_NAME"]
)
myCursor=mydb.cursor(dictionary=True)

def send_reset_email(user_email):
    token = secrets.token_urlsafe(32)
    update_query="UPDATE users SET token = %s WHERE email =%s"
    myCursor.execute(update_query,(token,user_email))
    mydb.commit()
    reset_link = f"http://localhost:5000/reset-password/{token}?email={user_email}"

    msg = EmailMessage()
    msg['Subject'] = 'Reset Your Password'
    msg['From'] = config["EMAIL"]
    msg['To'] = user_email
    msg.set_content(f'Click this link to reset your password: {reset_link}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config["EMAIL"], config["APP_PASSWORD"])
        smtp.send_message(msg)
