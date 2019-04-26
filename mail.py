import smtplib
import getpass

smtpObj = smtplib.SMTP('smtp.dtcc.edu', 587)  # or port 587 if on a VM b/c port 25 is blocked
smtpObj.ehlo()
smtpObj.starttls()

username = input("Enter your username: ")  # or raw
pw = getpass.getpass("Enter your password: ")
smtpObj.login(username + "@dtcc.edu", pw)

fro = input("From: ")+"@dtcc.edu"
to = input("To: ")+"@dtcc.edu"
subj = input("Subject: ")
body = input("Body: ")
msg = "Subject: " + subj + "\n" + body  # needs keyword Subject


smtpObj.sendmail(fro, to, msg)

smtpObj.quit()

