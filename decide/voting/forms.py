from django import forms
from .models import Voting


class ReuseCensusForm(forms.Form):
    voting_source = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Source_Voting', )
    voting_receiver = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Reciever_Voting')