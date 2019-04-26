import smtplib
import getpass
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

fileToSend = input("File to send: ")

msg = MIMEMultipart()
msg["From"] = input("From: ")+"@dtcc.edu"
msg["To"] = input("To: ")+"@dtcc.edu"
msg["Subject"] = input("Subject: ")

#html formatted body with tags for styling
body = """\
<html>
	<body>
		<p>we did it</p>
	</body>
</html>
"""
body = MIMEText(body, 'html')

#plain text body for simple text
body2 = input("Body: ")
body2 = MIMEText(body2, 'plain'))



ctype, encoding = mimetypes.guess_type(fileToSend)
if ctype is None or encoding is not None:
    ctype = "application/octet-stream"

maintype, subtype = ctype.split("/", 1)

if maintype == "text":
	#no extension attaches, text embeds as body and txt encodes charset
     fp = open(fileToSend)
     # Note: we should handle calculating the charset
     attachment = MIMEText(fp.read(), _subtype=subtype)
     fp.close()
elif maintype == "image":
     fp = open(fileToSend, "rb")
     attachment = MIMEImage(fp.read(), _subtype=subtype)
     fp.close()
elif maintype == "audio":
     fp = open(fileToSend, "rb")
     attachment = MIMEAudio(fp.read(), _subtype=subtype)
     fp.close()
else:
	fp = open(fileToSend, "rb")
	attachment = MIMEBase(maintype, subtype)
	attachment.set_payload(fp.read())
	fp.close()

encoders.encode_base64(attachment)
attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)

#HAVE TO SELECT WHICH BODY TYPE HERE
msg.attach(body2)
msg.attach(attachment)




smtpObj = smtplib.SMTP('smtp.dtcc.edu', 25)
smtpObj.ehlo()
smtpObj.starttls()
username = input("Enter your username: ") # or raw
pw = getpass.getpass("Enter your password: ")
smtpObj.login(username + "@dtcc.edu", pw)




smtpObj.sendmail(msg["From"],msg["To"], msg.as_string())
smtpObj.quit()

