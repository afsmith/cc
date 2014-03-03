PAYMENTS_PLANS = {
    "monthly": {
        "stripe_plan_id": "monthly",
        "name": "Kneto (150/month)",
        "description": "Monthly subscription to Kneto.",
        "price": 150,
        "currency": "eur",
        "interval": "month"
    },
    "yearly": {
        "stripe_plan_id": "beta-yearly",
        "name": "Kneto (1500/year)",
        "description": "Yearly subscription to Kneto.",
        "price": 1500,
        "currency": "eur",
        "interval": "year"
    },
    "monthly-trial": {
        "stripe_plan_id": "monthly-trial",
        "name": "Monthly subscription to Kneto. 30day trail",
        "description": "Monthly subscription to Kneto.",
        "price": 150,
        "currency": "eur",
        "interval": "month",
        "trial_period_days": 30
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