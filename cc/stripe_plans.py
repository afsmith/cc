# -*- coding: utf-8 -*-

PAYMENTS_INVOICE_FROM_EMAIL = 'cc@kneto.com'

PAYMENTS_PLANS = {
    'monthly': {
        'stripe_plan_id': 'monthly',
        'name': 'Single User',
        'description': 'Monthly subscription to Kneto.',
        'price': 184.76,
        'currency': 'eur',
        'interval': 'month',
        'interval_count': 1,
        'metadata': {
            'VAT': 35.76,
            'users': 1
        }
    },
    'early_small': {
        'stripe_plan_id': 'early_small',
        'name': 'Early Access small plan',
        'description': 'Early Access for three months, Three users',
        'price': 556.76,
        'currency': 'eur',
        'interval': 'month',
        'interval_count': 3,
        'metadata': {
            'VAT': 107.76,
            'users': 5
        }
    },
    'early_large': {
        'stripe_plan_id': 'early_large',
        'name': 'Early Access large plan',
        'description': 'Early Access for three months, Ten users',
        'price': 1858.76,
        'currency': 'eur',
        'interval': 'month',
        'interval_count': 3,
        'metadata': {
            'VAT': 359.76,
            'users': 12
        }
    },
}
