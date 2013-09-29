EMAIL_TEMPLATE = '''%(message)s.

Click here to check the file: %(ocl_link)s'''

CC_ME_TEMPLATE = '''Here is a copy of the message you sent to: %(recipients)s.
------------------------------------------------

%(message)s.

Click here to check the file: [link]

Best,
Kneto'''

NOTIFICATION_EMAIL_OPENED_TEMPLATE = '''%(recipient)s opened your email "%(subject)s".

If you selected to be notified when they look at your attachment we'll send you another email at that time.

Good closings to you.

Best,
Kneto'''

NOTIFICATION_LINK_CLICKED_TEMPLATE = '''%(recipient)s checked your attachment from email "%(subject)s."

Good closings to you.

Best,
Kneto'''

NOTIFICATION_CONVERSION_ERROR_TEMPLATE = '''The attachment from your email "%(subject)s." has encountered a conversion error.

Please try again or contact support@kneto.com.

Best,
Kneto'''
