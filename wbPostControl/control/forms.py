from django import forms
from control.models import Account

class AccountForm(forms.ModelForm):
    username=forms.CharField(max_length=20,help_text='username')
    password=forms.CharField(max_length=20,help_text='password')
    interest=forms.CharField(max_length=40,help_text='interest',widget=forms.HiddenInput(),required=False)
    start_time=forms.DateField(widget=forms.HiddenInput(),required=False)
    end_time=forms.DateField(widget=forms.HiddenInput(),required=False)
    liveness=forms.IntegerField(widget=forms.HiddenInput(),required=False)

    class Meta:
        model = Account
        fields = ['username','password','interest']

class EditForm(forms.Form):
    interest = forms.CharField(max_length=40,help_text='interest',required=False)
    start_time=forms.DateField(help_text='start_time',required=False)
    end_time=forms.DateField(help_text='end_time',required=False)
    liveness=forms.IntegerField(help_text='liveness',required=False)
