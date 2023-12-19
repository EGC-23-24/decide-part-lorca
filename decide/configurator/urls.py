from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.configurator,
        name="configurator"),
    path(
        "create_classic/",
        views.CreateClassicView.as_view(),
        name="create_classic"),
    path(
        "create_yes_no/",
        views.CreateYesNoView.as_view(),
        name="create_yes_no"),
    path(
        "create_multiple_choice/",
        views.CreateMultipleChoiceView.as_view(),
        name="create_multiple_choice",
    ),
    path(
        "create_preference/",
        views.CreatePreferenceView.as_view(),
        name="create_preference",
    ),
    path(
        "create_open_question/",
        views.CreateOpenQuestionView.as_view(),
        name="create_open_question",
    ),
    path(
        "manage_census/",
        views.ManageCensusView.as_view(),
        name="manage_census"),
]
