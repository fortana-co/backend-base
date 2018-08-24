from typing import List

from celery import shared_task

from helpers.http import get_ses_client


@shared_task(name='send_email', default_retry_delay=60, max_retries=3)
def send_email(
    to: List[str],
    subject: str,
    body: str,
    source: str = 'Notifications <email@address.com>',
    reply_to: List[str] = None,
    **kwargs,
):
    return get_ses_client().send_email(
        Source=source,
        Destination={
            'ToAddresses': to,
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8',
            },
            'Body': {
                'Html': {
                    'Data': body,
                    'Charset': 'UTF-8',
                }
            }
        },
        ReplyToAddresses=reply_to or [],
    )
