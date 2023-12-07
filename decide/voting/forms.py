from django import forms
from .models import Voting

class VotingSelectionForm(forms.Form):
    votation = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Select a voting')
