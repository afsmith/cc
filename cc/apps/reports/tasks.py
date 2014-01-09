from .models import Bounce
from cc.libs.sendgrid import sendgrid_get_bounces_list

from celery.decorators import task
#from datetime import datetime, timedelta


@task
def fetch_bounces_OLD():
    '''
    Periodical task to fetch bounces from Sendgrid
    '''
    # get last value in DB to pull out the start date to fetch
    try:
        last = Bounce.objects.latest('created_at')
        start_date = last.created_at.strftime('%Y-%m-%d')
    except Bounce.DoesNotExist:
        start_date = None

    # fetch list of bounces from sendgrid
    items = sendgrid_get_bounces_list(start_date)
    for item in items:
        # use get_or_create to avoid duplicates
        b, created = Bounce.objects.get_or_create(
            email=item.get('email'),
            status=item.get('status'),
            reason=item.get('reason'),
            created_at=item.get('created'),
        )
