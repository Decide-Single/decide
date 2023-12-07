from django.urls import path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('process-and-compress-voting/', views.process_and_compress_voting, name='process_and_compress_voting'),
]
