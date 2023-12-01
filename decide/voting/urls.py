from django.urls import path
from . import views
from .views import ReuseCensusView


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('reuse_census/', ReuseCensusView.as_view(), name='reuse_census'),
]
