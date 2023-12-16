from django.urls import path, include
from . import views
from .views import census

urlpatterns = [
    path("", views.CensusCreate.as_view(), name="census_create_api"),
    path("<int:voting_id>/", views.CensusDetail.as_view(), name="census_detail"),
    path("export/", views.CensusExportView.as_view(), name="export_census"),
    path("export/<int:voting_id>/", views.export_census, name="export_census_of_voting"),
    path("import/", views.CensusImportView.as_view(), name="import_census"),

    path('details/',views.GetId, name='census_details'),
    path("census/", views.census, name="census"),
    path('create/', views.createCensus, name='census_create'),
    path('census_list/', views.censusList, name='census_list'),
    path('delete/', views.deleteCensus, name='census_deleted')
]