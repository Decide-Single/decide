from django.views import View
import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics, status
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer, QuestionSerializer
from base.perms import UserIsStaff
from base.models import Auth
from .forms import ReuseCensusForm, QuestionForm, QuestionOptionFormSet

class QuestionView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend)
    filterset_fields = ('id',)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)

        for data in ['desc', 'question_type', 'options']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('desc'), question_type=request.data.get('question_type'))
        question.save()

        if question.question_type == 'YESNO':
            yes_opt = QuestionOption(question=question, option='Yes', number=1)
            no_opt = QuestionOption(question=question, option='No', number=2)
            yes_opt.save()
            no_opt.save()
        else:
            for idx, q_opt in enumerate(request.data.get('options')):
                opt = QuestionOption(question=question, option=q_opt, number=idx)
                opt.save()

        return Response({}, status=status.HTTP_201_CREATED)

class QuestionList(TemplateView):
    permission_classes = [IsAdminUser]

    def get(request):
        if request.user.is_staff:
            questions = Question.objects.all()
            return render(request, 'question_list.html', {'questions': questions})
        else:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

class QuestionCreation(TemplateView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        if request.user.is_staff:
            form = QuestionForm()
            formset = QuestionOptionFormSet(prefix='options', queryset=QuestionOption.objects.none())
            return render(request, 'question_add.html', {'form': form, 'formset': formset})
        else:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        if request.user.is_staff:
            form = QuestionForm(request.POST)
            formset = QuestionOptionFormSet(request.POST, prefix='options')
            
            if form.is_valid() and formset.is_valid():
                question = form.save()
                if question.question_type == 'YESNO':
                    yes_opt = QuestionOption(question=question, option='Yes', number=1)
                    no_opt = QuestionOption(question=question, option='No', number=2)
                    yes_opt.save()
                    no_opt.save()
                else:
                    options = formset.save(commit=False)
                    for option in options:
                        option.question = question
                        option.number = options.index(option) + 1
                        option.save()
                return redirect('question_list')
        else:
            return Response({}, status=status.HTTP_403_FORBIDDEN)

class QuestionDelete(TemplateView):
    permission_classes = [IsAdminUser]

    def post(self, request, question_id):
        if request.user.is_staff:
            question = get_object_or_404(Question, pk=question_id)
            question.delete()
            return redirect('question_list')
        else:
            return Response({}, status=status.HTTP_403_FORBIDDEN)
        
class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('id', )

    def get(self, request, *args, **kwargs):
        idpath = kwargs.get('voting_id')
        self.queryset = Voting.objects.all()
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'question', 'question_type', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('question'), question_type=request.data.get('question_type'))
        question.save()
        for idx, q_opt in enumerate(request.data.get('question_opt')):
            opt = QuestionOption(question=question, option=q_opt, number=idx)
            opt.save()
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),
                question=question)
        voting.save()

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)


class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'

        return Response(msg, status=st)

class ReuseCensusView(View):
    template_name = "reuse_census.html"

    def get(self, request, *args, **kwargs):
        votings= Voting.objects.all()
        return render(request,self.template_name,{'votings':votings})

    def post(self, request, *args, **kwargs):
        votings= Voting.objects.all()
        if request.method == 'POST':
            form = ReuseCensusForm(request.POST)
            print(form.errors)
            if form.is_valid():
                source = form.cleaned_data['voting_source']
                reciever = form.cleaned_data['voting_receiver']
                if reciever.end_date:
                    messages.error(request, 'La votación de destino ya ha finalizado.')
                elif source==reciever:
                    messages.error(request, 'La votación de origen y destino no pueden ser la misma.')
                else:
                    source.add_census_to_another_votings(reciever)
                    return redirect('http://localhost:8000/admin/voting/voting/')
            else:
                messages.error(request, 'El formulario no es válido. Por favor, corrige los errores.')
        return render(request, self.template_name, {'form': form, 'votings':votings})

