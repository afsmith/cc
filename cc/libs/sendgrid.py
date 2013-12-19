from django.conf import settings

import requests

# http://sendgrid.com/docs/API_Reference/Web_API/index.html
API_URL = 'https://api.sendgrid.com/api/'
SENDGRID_USER = 'andrew.smith@kneto.com'
SENDGRID_PW = 'rFUnDlfNA5l)[ncu\'IN6N.P!R'


def get_bounces_list(): 
    url = API_URL + 'bounces.get.json'

    post_data = {
        'api_user': SENDGRID_USER,
        'api_key': SENDGRID_PW,
        'date': 1
    }
    r = requests.post(url, data=post_data)

    return r.json()
