from django import forms

from payments.settings import PLAN_CHOICES


class PlanForm(forms.Form):
    # pylint: disable=R0924
    plan = forms.ChoiceField(choices=PLAN_CHOICES + [("", "-------")])
    #plan = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class':'btn btn-default'}), choices=PLAN_CHOICES + [("", "None")])
    #plan = forms.ChoiceField(widget=forms.RadioSelect(attrs={'class':'btn btn-default'}), choices=PLAN_CHOICES + [("", "None")])

