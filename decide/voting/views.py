import json
import os
import zipfile

import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response

from .forms import VotingSelectionForm
from .models import Question, QuestionOption, Voting
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth


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
        for data in ['name', 'desc', 'question', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('question'))
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
        elif action == 'copy_census':
            if voting.end_date:
                msg = 'Voting has already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.add_census_to_another_votings(request.auth.key)
                msg = 'Census succesfully copied into one another'
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)

def process_and_compress_voting(request):
    redirect_to = request.META.get('HTTP_REFERER', '/')
    if request.method == 'POST':
        form = VotingSelectionForm(request.POST)
        if form.is_valid():
            selected_voting = form.cleaned_data['votation']

            voting_data = {
                'id': selected_voting.id,
                'name': selected_voting.name,
                'description': selected_voting.desc,
                'start_date': selected_voting.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'end_date': selected_voting.end_date.strftime('%Y-%m-%d %H:%M:%S'),
                'tally': selected_voting.tally,
            }

            result_txt_path = os.path.join(settings.STATIC_ROOT, f'voting_result_{selected_voting.id}.txt')
            with open(result_txt_path, 'w') as result_txt_file:
                result_txt_file.write(json.dumps(voting_data))

            result_zip_path = os.path.join(settings.STATIC_ROOT, f'voting_result_{selected_voting.id}.zip')
            with zipfile.ZipFile(result_zip_path, 'w') as zipf:
                zipf.write(result_txt_path, arcname=f'voting_result_{selected_voting.id}.txt')

            os.remove(result_txt_path)

            success_message = 'File generated and saved successfully!'
            form = VotingSelectionForm()
            return render(request, 'voting_selection.html', {'message': success_message, 'form': form})
    else:
        form = VotingSelectionForm()
    return render(request, 'voting_selection.html', {'form': form})