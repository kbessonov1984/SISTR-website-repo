#! /usr/bin/python3
import smtplib, argparse

def arguments():


    parser = argparse.ArgumentParser(
        description="Send Gmail notification simple utility")
    parser.add_argument('-e',
                        default='',
                        help='Email of a recipient')

    parser.add_argument('-t',
                        default='',
                        help='Job token')


    args = parser.parse_args()

    return args

gmail_user = 'kbessono@gmail.com'
gmail_password = 'kiri1984!'
SISTR_URL='XXXXX'

def compose_email(token):
    sent_from = gmail_user
    send_to = ['kbessonov@gmail.com']
    subject = 'SISTR: Your job {} is ready'.format(token)
    body = 'Dear user,\nPlease download your results from {} using token {}\n\nSincerely,\nSISTR TEAM'.format(SISTR_URL, token)

    email_text = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (
           sent_from,
           ", ".join(send_to),
           subject,
           body
    )

    return sent_from, send_to, email_text

try:
    args = arguments()

    if args.e and args.t:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)

        sent_from, sent_to, email_text = compose_email(args.t)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print ('Email successfully sent!')
    else:
        raise("Email or Token not defined. Their values were email:{} and token:{}".format(args.e, args.t))
except Exception as e:
    print ('Something went wrong... {}'.format(e))