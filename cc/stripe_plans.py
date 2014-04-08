# -*- coding: utf-8 -*-

PAYMENTS_INVOICE_FROM_EMAIL = 'cc@kneto.com'

PAYMENTS_PLANS = {
    'monthly': {
        'stripe_plan_id': 'monthly',
        'name': 'Single User',
        'description': 'Monthly subscription to Kneto.',
        'price': 24.78,
        'currency': 'eur',
        'interval': 'month',
        'interval_count': 1,
        'metadata': {
            'VAT': 4.79,
            'users': 1
        }
    },
    'early_small': {
        'stripe_plan_id': 'early_small',
        'name': 'Early Access small plan',
        'description': 'Early Access, Five users',
        'price': 186.00,
        'currency': 'eur',
        'interval': 'month',
        'interval_count': 1,
        'metadata': {
            'VAT': 36.00,
            'users': 5
        }
    },
    'early_large': {
        'stripe_plan_id': 'early_large',
        'name': 'Early Access large plan',
        'description': 'Early Access, Twelve users',
        'price': 618.76,
        'currency': 'eur',
        'interval': 'month',
        'interval_count': 1,
        'metadata': {
            'VAT': 119.76,
            'users': 12
        }
    },
}
