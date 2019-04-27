# Collin Craig
# ISY 150-4W1
# 4/24/2018 (Version 1.0)

# "Congressional Districting" #

import csv
import json
import requests
# used for graphing purposes
import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.pyplot as plt
# used for mailing
import smtplib
import getpass
import time # imported to use sleep function with getpass() not running on pycharm
from pyshorteners import Shortener
import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Unordered Notes #
# Using a fake CSV file with fake info to test the script, the file is in the format name,address,email.
# Yup once again pycharm I know that variable and function names are to be lowercase but I like camelcase

# Function Definitions #


def parseCSV(name):  # This function will parse a CSV file into a python dictionary
    with open(name, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        students = []
        for row in csv_reader:
            # attempt to geocode location and add to ordered dict during parsing
            tempGeoCoords = geocodeAddress(row['address'])
            tempCoordsx = tempGeoCoords[0]
            tempCoordsy =tempGeoCoords[1]
            row.update({"lat": tempCoordsx})
            row.update({"long": tempCoordsy})
            # end of attempt & it worked xD
            students.append(row)
    return students


def printStudents(listOfStudents):
    studentNumber = 0
    for student in listOfStudents:
        studentNumber += 1
        print(student)
        #for key, value in student.items():
            #print("Student Number: " + str(studentNumber) + " " + key + ": " + value)


def printReps(listOfReps):
    for rep in listOfReps:
        for key, value in rep.items():
            print(key +" & "+value)


def geocodeAddress(addyIn):
    apiKey = "koBSx5A8tI3GQVXABdi6F7vGNdhwiESn"
    concatUrl = "http://www.mapquestapi.com/geocoding/v1/address?key=" + apiKey + "&location=" + addyIn
    #webbrowser.open(concatUrl)
    req = requests.get(concatUrl)
    data = json.loads(req.text)
    coords = [(str(data['results'][0]['locations'][0]['latLng']["lat"])), str(data['results'][0]['locations'][0]['latLng']["lng"])]
    #print("Processed address coords: " + coords[0] + "," + coords[1])
    return coords


def findLegislatorInfo(listOfStudents):
    listOfReps = []
    for student in listOfStudents:
        repsForStudent = []
        lat = student["lat"]
        long = student["long"]
        headers = {'X-API-KEY': '7857645c-5b7c-4a1c-946b-19a06b25321c'}
        concatUrl = "http://openstates.org/api/v1/legislators/geo/?lat="+lat+"&long="+long
        #print(concatUrl)
        req = requests.get(concatUrl, headers=headers)
        data = json.loads(req.text)
        for i in range(len(data)):  # for each rep
            offices = data[i]["offices"]
            # find first office address and phone number that is not null
            for x in range(len(offices)):
                if offices[x]["address"] is not None:
                    repAddress = offices[x]["address"]
                if offices[x]["phone"] is not None:
                    repPhone = offices[x]["phone"]
            repName = data[i]["full_name"]
            #print(repName + " @ " + repAddress + " # " + repPhone)
            tempStorage = {"RepName": repName, "RepAddress": repAddress, "RepPhone": repPhone}
            tempStorageName = tempStorage["RepName"]
            listOfReps.append(tempStorage)
            repsForStudent.append(tempStorageName)
        #print("Associating reps with student: "+student["name"]+" and reps "+str(repsForStudent))
        student.update({"reps": repsForStudent})
    return listOfReps, listOfStudents


def declutter(listOfReps):
    reps = []
    for i in range(len(listOfReps)):
        if listOfReps[i] not in listOfReps[i + 1:]:
            reps.append(listOfReps[i])
    return reps


def confirmMapLink(listOfStudents):
    apiKey = "koBSx5A8tI3GQVXABdi6F7vGNdhwiESn"
    for student in listOfStudents:
        concatUrl = "https://www.mapquestapi.com/staticmap/v4/getmap?key=" \
                + apiKey + "&size=600,600&type=map&imagetype=jpg&zoom=17&" \
                + "scalebar=false&traffic=false&center=" + student["lat"] + "," + student["long"] \
                + "&xis=https://as2.ftcdn.net/jpg/01/38/35/43/500_F_138354315_IWMZOLF07k7WIQaIMFNbZDjPkFGgG63O.jpg" \
                + ",1,c," + student["lat"] + "," + student["long"] + "&ellipse=fill:0x70ff0000|color:0xff0000|" \
                "width:2|40.00,-105.25,40.04,-105.30"
        #print("Map Confirmation Link for student "+student["name"]+" - "+concatUrl)
        student.update({'maplink': concatUrl})
    return listOfStudents


def createBarGraph(listOfStudents, noDupesReps):
    # attempt to count number of students per rep
    studentsPerRep = {}
    for rep in noDupesReps:
        studentsPerRep.update({rep['RepName']: 0})
    #print(studentsPerRep)
    for student in listOfStudents:
        for i in range(len(student['reps'])):
            #print("Student "+student['name']+" for rep "+student['reps'][i])
            studentsPerRep.update({student['reps'][i]: studentsPerRep[student['reps'][i]]+1})
    #print(studentsPerRep)
    # end of attempt and worked xD

    plt.bar(range(len(studentsPerRep)), list(studentsPerRep.values()), align='center')
    plt.xticks(range(len(studentsPerRep)), list(studentsPerRep.keys()), rotation='vertical')
    plt.ylabel('Number of Students')
    plt.title('Students per Rep')

    plt.show()


def createEmail(listOfStudents, noDupeReps):
    print("In order for this script to work, you must login to your dtcc account to"
          + " send the mail. \nI was not about to hardcode my details in to make it"
          + " automatic.")
    smtpObj = smtplib.SMTP('smtp.dtcc.edu', 587, timeout=120)
    smtpObj.ehlo()
    smtpObj.starttls()

    # had to add because of stupid ascii restrictions
    replacements = {0x2018: "'",
                    0x2019: "'",
                    0x2013: '-',
                    0x2026: '...'}

    username = input("Enter your username: ")
    pw = getpass.getpass("Enter your password: ")
    smtpObj.login(username + "@dtcc.edu", pw)
    fro = "noreply@dtcc.edu"
    subj = "VOTE ‘Yes’ on Proposition 611"
    shortener = Shortener('Tinyurl')
    for student in listOfStudents:
        attachmentDocs = createAttachment(student, noDupeReps)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subj
        msg['From'] = fro
        to = student["email"]
        msg['To'] = to
        studentName = {student["name"]}
        studentName = str(studentName).replace("{", "").replace("'", "").replace("}", "")
        mapLink = {student["maplink"]}
        mapLink = str(mapLink).replace("{", "").replace("'", "").replace("}", "")
        finalLink = "{}".format(shortener.short(mapLink))
        # print("My short url is {}".format(shortener.short(mapLink)))
        body = """ Dear, {0} \n \
                I hope you are having a wonderful day today, we are reaching out to you asking you to vote YES on \
Proposition 611. This new House bill will allow the state to earmark money for students who \
need financial assistance while taking college courses. We have automatically generated an \
attachment for you to send to your state legislators, which we have already personalized for your \
particular district- we have made it easy on you so all we are asking is for you to sign and send \
it! \
Just to make sure we have done this correctly, here is a generated link confirming your location \
that we have on school records; {1} 
We thank you for your time and hope you can take the extra steps to make sure this proposition \
gets passed. 
Have a nice day {0}! 
*this is an auto-generated message on behalf of dtcc.edu* 
**by the way, this message is fake and for a class project if you somehow actually got this \
email to disregard it as this was not a real message sent from the school** 
"""
        body = body.format(studentName, finalLink)
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)
        for i in range(len(attachmentDocs)):
            filename = attachmentDocs[i]
            fo = open(filename, 'rb')
            attach = email.mime.application.MIMEApplication(fo.read(), _subtype="pdf")
            fo.close()
            attach.add_header('Content-Disposition', 'attachment', filename=filename)
        msg = "Subject: " + subj + "\n\n" + body  # needs keyword Subject
        smtpObj.sendmail(fro, to, msg.translate(replacements))
        print("Successfully email letter to: " + student["email"])
        time.sleep(2) # had to add due to restrictions with URL shortener

    smtpObj.quit()


def createAttachment(student, noDupeReps):
    attachmentDocs = []
    for i in range(len(student['reps'])):
        print("Creating PDF letter for "+student['name']+" to send to rep "+student['reps'][i])

        doc = SimpleDocTemplate("letter_"+student['reps'][i]+"_by_"+student['name']+".pdf", pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)
        Story = []
        for rep in noDupeReps:
            if rep["RepName"] == student['reps'][i]:
                #print("Matched "+rep['RepName']+" with "+student['reps'][i])
                formatted_time = time.ctime()
                full_name = rep["RepName"]
                address_parts = re.split(r"\.\s*", rep["RepAddress"])
                styles = getSampleStyleSheet()
                styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
                ptext = '<font size=12>%s</font>' % formatted_time

                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 12))

                ptext = '<font size=12>%s</font>' % full_name
                Story.append(Paragraph(ptext, styles["Normal"]))
                for part in address_parts:
                    ptext = '<font size=12>%s</font>' % part.strip()
                    Story.append(Paragraph(ptext, styles["Normal"]))

                Story.append(Spacer(1, 12))
                ptext = '<font size=12>Dear %s:</font>' % full_name.split()[0].strip()
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 12))

                ptext = '<font size=12>I am voting YES for proposition 611 to allow the state to earmark money for students who \
need financial assistance while taking college courses.</font>'

                Story.append(Paragraph(ptext, styles["Justify"]))
                Story.append(Spacer(1, 12))

                ptext = '<font size=12>Thank you for your time and for reading this letter.</font>'
                Story.append(Paragraph(ptext, styles["Justify"]))
                Story.append(Spacer(1, 12))
                ptext = '<font size=12>Sincerely,</font>'
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 24))
                ptext = '<font size=12>%s</font>' % student['name']
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 12))
                ptext = '<font size=12>X_______________________________</font>'
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1,24))
                doc.build(Story)
                attachmentDocs.append("letter_"+student['reps'][i]+"_by_"+student['name']+".pdf")
    return attachmentDocs


def main():
    listOfStudents = parseCSV("first.csv")  # returns a list of dictionaries containing students info
    #printStudents(listOfStudents)
    listOfReps, listOfStudents = findLegislatorInfo(listOfStudents)
    noDupesReps = declutter(listOfReps)
    listOfStudents = confirmMapLink(listOfStudents)
    #printStudents(listOfStudents)
    createBarGraph(listOfStudents, noDupesReps)
    createEmail(listOfStudents, noDupesReps)

# Function Calls #
main()
