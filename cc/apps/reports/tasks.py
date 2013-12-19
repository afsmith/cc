from .models import Bounce
from cc.libs.sendgrid import get_bounces_list

from celery.decorators import task
#from datetime import datetime, timedelta


@task
def fetch_bounces():
    '''
    Periodical task to fetch bounces from Sendgrid
    '''

    items = get_bounces_list()
    bounces = []
    for item in items:
        # TODO: check duplicated item here
        items.append(Bounce(
            email=item.get('email'),
            status=item.get('status'),
            reason=item.get('reason'),
            created_at=item.get('created'),
        ))

    Bounce.objects.bulk_create(bounces)
