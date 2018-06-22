import os
import boto3
import csv
import time
import json
import datetime
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event, context):
    
    client = boto3.client('iam')
    #Generating Credential Report.
    response = client.generate_credential_report()
    #Setting date for the report.
    today = datetime.date.today().strftime("%B-%d-%Y")
    
    print("\nGenerating AWS Credential Report on {}.....\n".format(today) )
    #Setting wait time so report generation can be finished before getting the report.
    w_time = 0
    
    while response['State'] != 'COMPLETE':
        w_time += 1
        print("Waiting...{}\n".format(w_time))
        time.sleep(w_time)
        print("Credential Report is ready.\n")
    #Getting generated report.
    report = client.get_credential_report()
    
    print("Getting IAM report from Credential Report.....\n")
    #Creating empty list.  The report returns dictionary and only the IAM users and roles are needed.
    iam_report = []
    #Appending value under Content which is actual IAM users and roles.
    iam_report.append(report['Content'].decode('utf-8'))
    
    #Setting variable for filename and creating empty csv file to store list of IAM users and roles.
    iam_csv = 'IAM_Report_' + today + '.csv'
    csvfile = '/tmp/' + iam_csv
    
    #Creating IAM credential report in csv format.
    with open(csvfile, 'w') as myfile:
        writer = csv.writer(myfile, delimiter=' ', quotechar=' ', lineterminator='\n')
        for i in iam_report:
            writer.writerow([i])
    
    #Storing csv file to S3 bucket.
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(csvfile, 'temp-restore', iam_csv)
    
    #Sending an email to AWS Support distro with csv attachment.
    SENDER = "noreply@cfpb.gov"
    RECIPIENT = "_DL_CFPB_SystemsEngineeringAWSSupport@cfpb.gov"
    SUBJECT = "IAM Credential Report on " + today
    ATTACHMENT = csvfile
    BODY_TEXT = "Hello,\r\n\nPlease see the attached file for a list of IAM users and roles."
    CHARSET = "utf-8"
 
    client = boto3.client('ses')
    
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    
    msg_body = MIMEMultipart('alternative')
    
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    
    msg_body.attach(textpart)
    
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())
    
    att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(ATTACHMENT))
    
    msg.attach(msg_body)
    
    msg.attach(att)
    
    try:
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECIPIENT
            ],
            RawMessage={
                'Data': msg.as_string(),
            },
        )
    #Raise error if email was not sent.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID: {}\n".format(response['MessageId'])),
        
    return
    
