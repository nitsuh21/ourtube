from django import forms

Role= [
    ('is_Viewer', 'Viewer'),
    ('is_Creator', 'Creator')
    ]
PRIVACY_CHOICES = [
        ("username","username"),
        ("channel","channel"),
        ("socialmedia","socialmedia")
]

class UserForm(forms.Form):
    role= forms.CharField(label='SignUp as', widget=forms.RadioSelect(choices=Role))
class PrivacyForm(forms.Form):
    privacy = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=PRIVACY_CHOICES)
