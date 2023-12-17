from .utils import future_stop_task_manager
import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Question, QuestionOption, Voting
from census.models import Census
from .serializers import SimpleVotingSerializer, VotingSerializer
from base.perms import UserIsStaff
from base.models import Auth
from django.utils import timezone
from voting.models import Voting
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import  UpdateVotingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
            question=question, future_stop=request.data.get('future_stop'))
    voting.save()

    auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                      defaults={'me': True, 'name': 'test auth'})
    auth.save()
    voting.auths.add(auth)

    future_stop_task_manager(voting.id)
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
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)
    



@login_required(login_url="/authentication/login-view/")
def list_votings(request):
    if request.user.is_staff:
        votings = Voting.objects.all()
        user = request.user
        return render(request, 'list_votings.html', {
            'votings': votings,
            'user': user,
        })
    else:
        census =  Census.objects.filter(voter_id=request.user.id)
        votings = Voting.objects.filter(id__in=census.values('voting_id'))
        user = request.user
        return render(request, 'list_votings.html', {
            'votings': votings,
            'user': user,
        })

@login_required(login_url="/authentication/login-view/")
def voting_details(request,voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    return render(request, 'voting_details.html',{
        'voting': voting,
    })

@login_required(login_url="/authentication/login-view/")
def voting_delete(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)

    if request.method == 'POST':
        
        if 'delete_button' in request.POST:
            
            voting.delete()
            messages.success(request, 'La votación ha sido eliminada con éxito.')
            return redirect('list_votings')  

    return render(request, 'list_votings.html', {'votings': Voting.objects.all(), 'user': request.user})

@login_required(login_url="/authentication/login-view/")
def start_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    if request.method == 'POST':
        if 'start_voting_button' in request.POST:
            voting.create_pubkey()
            voting.start_date = timezone.now()
            voting.save()
            messages.success(request, 'Voting started successfully.')
            return redirect('list_votings')  
    return render(request, 'list_votings.html', {'votings': Voting.objects.all(), 'user': request.user})


@login_required(login_url="/authentication/login-view/")
def end_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    if request.method == 'POST':
        if 'end_voting_button' in request.POST:
            voting.end_date = timezone.now()
            voting.save()
            messages.success(request, 'Voting started successfully.')
            return redirect('list_votings')  
    return render(request, 'list_votings.html', {'votings': Voting.objects.all(), 'user': request.user})

@login_required(login_url="/authentication/login-view/")
def update_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)

    if request.method == 'POST':
        form = UpdateVotingForm(request.POST, instance=voting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voting updated successfully.')
            return redirect('list_votings')  
    else:
        form = UpdateVotingForm(instance=voting)

    return render(request, 'update_voting.html', {'form': form, 'voting': voting})

@login_required(login_url="/authentication/login-view/")
def tally_view(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    if request.method == 'POST':
        token = request.session.get('auth-token', '')
        voting.tally_votes(token)
        messages.success(request, 'Tally completed successfully.')
        return redirect('list_votings')  

    return render(request, 'tally_view.html', {'voting': voting})