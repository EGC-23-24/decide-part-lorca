from visualizer.views import VisualizerView
from booth.views import BoothView
from django.urls import path
from . import views
from .views import list_votings,voting_details,voting_delete,start_voting,end_voting,update_voting

urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('list_votings/',list_votings,name='list_votings'),
    path('list_votings/<int:voting_id>/',voting_details,name='voting_details'),
    path('list_votings/<int:voting_id>/delete/', voting_delete, name='voting_delete'),
    path('list_votings/<int:voting_id>/start/', start_voting, name='start_voting'),
    path('list_votings/<int:voting_id>/end/', end_voting, name='end_voting'),
    path('list_votings/<int:voting_id>/update/', update_voting, name='update_voting'),
    path('list_votings/<int:voting_id>/tally/', views.tally_view, name='tally_view'),
  
]