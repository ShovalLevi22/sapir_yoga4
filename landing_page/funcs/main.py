import traceback
import yagmail
from . resources import *


def read_html(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        return template_file.read()


def prepare_html(json, url_id):
    new_html = read_html(json['html_file_name'])
    if json:
        html_details = json['html']

        for key in html_details:
            new_html = new_html.replace('{' + key + '}', html_details[key])
        new_html = new_html.replace('{user_id}', url_id)
        return new_html.replace('\n', '')

    else:
        return new_html.replace('\n', '')


def send_mail(to, campaign_json, url_id):
    try:
        c_json = Myjson(campaign_json).get()

        # initializing the server connection
        yag = yagmail.SMTP(user=c_json['login']['User'], password=c_json['login']['Password'])

        # getting values into HTML
        fixed_html = prepare_html(c_json, url_id)

        # sending the email
        yag.send(to=to, subject=c_json['email_subject'], contents=fixed_html)
        print("Email sent successfully")

    except:
        traceback.print_exc()
        print("Error, email was not sent")


# send_mail(to='shovallevi.w@gmail.com',
#           subject='dd',
#           html_file='html/b.html',
#           client_json='Sapir.json')
