from django.urls import path, include
from . import views
from .views import CensusImportView

urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('import/', CensusImportView.as_view(), name='import_census'),
]
