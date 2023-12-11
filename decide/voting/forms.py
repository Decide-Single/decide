from django import forms
from .models import Voting, Question, QuestionOption

class ReuseCensusForm(forms.Form):
    voting_source = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Source_Voting', )
    voting_receiver = forms.ModelChoiceField(queryset=Voting.objects.all(), label='Reciever_Voting')

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['desc', 'question_type']

class QuestionOptionForm(forms.ModelForm):
    class Meta:
        model = QuestionOption
        fields = ['option']

QuestionOptionFormSet = forms.modelformset_factory(QuestionOption, form=QuestionOptionForm, extra=5)