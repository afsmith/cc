# -*- coding: utf-8 -*-

PAYMENTS_PLANS = {
    "monthly": {
        "stripe_plan_id": "monthly",
        "name": "Single User (€150/month)",
        "description": "Monthly subscription to Kneto.",
        "price": 150,
        "currency": "eur",
        "interval": "month"
    },
    "early_small": {
        "stripe_plan_id": "early_small",
        "name": "Early Access small plan",
        "description": "Early Access for three months, Three users",
        "price": 450,
        "currency": "eur",
        "interval": "month",
        "interval_count": 3,
    },
    "early_large": {
        "stripe_plan_id": "early_large",
        "name": "Early Access large plan",
        "description": "Early Access for three months, Ten users",
        "price": 1500,
        "currency": "eur",
        "interval": "month",
        "interval_count": 3,
    },

}