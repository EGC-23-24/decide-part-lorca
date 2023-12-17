from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import GetUserView, LogoutView, RegisterViewAPI, LoginView, RegisterView, logout_view, main


urlpatterns = [
    path('login-view/',LoginView.as_view(), name='login'),
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterViewAPI.as_view()),
    path('register-view/', RegisterView.as_view()),
    path('logout-view/',logout_view),
    path('',main),
]
