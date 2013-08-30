from django.conf import settings
from celery.decorators import task
from cc.apps.management.models import OneClickLinkToken
from datetime import date
import logging

logger = logging.getLogger("management")


@task
def check_ocl_expiration():
    results = OneClickLinkToken.objects.filter(expired=False,
            expires_on__lt=date.today())
    
    logger.debug("Found %s ocl's to expire" % results.count())
    for ocl in results:
        ocl.expired = True
        ocl.save()
        logger.debug("OCL %s expired" % ocl)
    logger.debug("done")


if __name__ == '__main__':
    check_ocl_expiration()
