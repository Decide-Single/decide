from django import forms
from .models import Voting, Question, QuestionOption
from django.core.exceptions import ValidationError


class ReuseCensusForm(forms.Form):
    voting_source = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Source_Voting', )
    voting_receiver = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Reciever_Voting')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['desc', 'question_type']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['desc'].label = "Describe your question in a couple of words. Ex. How's the day going?"

class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['option']
   
QuestionOptionFormSet = forms.modelformset_factory(QuestionOption, form=QuestionOptionForm, extra=2)    