import smtplib
from email.message import EmailMessage
import secrets
import mysql.connector

mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="anas123",
    database="expense_tracker"
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
    msg['From'] = 'anasqureshi6556@gmail.com'
    msg['To'] = user_email
    msg.set_content(f'Click this link to reset your password: {reset_link}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('anasqureshi6556@gmail.com', 'ybme bgrz qjrw zkut')
        smtp.send_message(msg)
