from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED
)
from django.http import HttpResponse
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django import forms
from .serializers import UserSerializer
import re
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration.

    Extends UserCreationForm to add custom validation methods for username and password.

    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'email',
            'first_name',
            'last_name'
        )

        labels = {
            'username': ('Username'),
            'password1': ('Password'),
            'password2': ('Confirm Password'),
            'email': ('Email'),
            'first_name': ('First Name'),
            'last_name': ('Last Name')
        }

    def username_clean_lenght(self, username):
        """
        Validate the length of the username.

        :param username: The username to be validated.
        :type username: str
        :return: True if the username is longer than 150 characters, False otherwise.
        :rtype: bool
        """
        username = username.lower()

        if len(username) > 150:
            return True
        else:
            return False

    def username_clean_exits(self, username):
        """
        Check if the username already exists in the database.

        :param username: The username to be checked.
        :type username: str
        :return: True if the username already exists, False otherwise.
        :rtype: bool
        """
        username = username.lower()

        new = User.objects.filter(username=username)
        if new.count():
            return True
        else:
            return False

    def username_clean_pattern(self, username):
        """
        Validate the username against a specific pattern.

        :param username: The username to be validated.
        :type username: str
        :return: True if the username does not match the pattern, False otherwise.
        :rtype: bool
        """
        username = username.lower()

        username_val_regex = re.search("[^\\w@.\\-_+]", username)
        if (username_val_regex is not None):
            return True
        return False

    def email_clean(self, email):
        """
        Check if the email already exists in the database.

        :param email: The email to be checked.
        :type email: str
        :return: True if the email already exists, False otherwise.
        :rtype: bool
        """
        email = email.lower()
        new = User.objects.filter(email=email)
        if new.count():
            return True
        return False

    def clean_confirmation(self, password, confirm_password):
        """
        Validate that the entered passwords match.

        :param password: The first entered password.
        :type password: str
        :param confirm_password: The second entered password for confirmation.
        :type confirm_password: str
        :return: True if the passwords do not match, False otherwise.
        :rtype: bool
        """
        if password and confirm_password and password != confirm_password:
            return True
        return False

    def clean_password_lenght(self, password):
        """
        Validate the length of the password.

        :param password: The password to be validated.
        :type password: str
        :return: True if the password has fewer than 8 characters, False otherwise.
        :rtype: bool
        """
        if len(password) < 8:
            return True
        else:
            return False

    def clean_password_common(self, password):
        """
        Check if the entered password is common.

        :param password: The password to be checked.
        :type password: str
        :return: True if the password is common, False otherwise.
        :rtype: bool
        """
        common_passwords = [
            '12345678',
            '11111111',
            '00000000',
            'password',
            'password0',
            'password1',
            'decide',
            'decide password',
            '01234567',
            '2345678',
            'password123',
            'password12',
            'cotraseña',
            'contraseña123',
            'adminadmin',
            'admin123',
            '1234567890',
            '0987654321',
            '87654321',
            'lorca123',
            'lorca_password']

        res = False
        for c in common_passwords:

            if (password == c):
                res = True
                break

        return res

    def clean_password_too_similar(
            self,
            password,
            username,
            first_name,
            last_name):
        """
        Check if the password is too similar to personal data.

        :param password: The password to be checked.
        :type password: str
        :param username: The username of the user.
        :type username: str
        :param first_name: The first name of the user.
        :type first_name: str
        :param last_name: The last name of the user.
        :type last_name: str
        :return: True if the password is too similar to personal data, False otherwise.
        :rtype: bool
        """
        if (password.__contains__(username) | password.__contains__(
                first_name) | password.__contains__(last_name)):
            return True

        else:
            return False

    def clean_password_numeric(self, password):
        """
        Check if the password consists only of numeric characters.

        :param password: The password to be checked.
        :type password: str
        :return: True if the password consists only of numeric characters, False otherwise.
        :rtype: bool
        """
        if (password.isnumeric()):
            return True
        else:
            return False


class GetUserView(APIView):
    """
    API view for retrieving user information.

    Handles POST requests to retrieve user information based on the provided user token.

    """

    def post(self, request):
        """
        Handle POST requests to retrieve user information.

        :param request: The incoming HTTP request containing the user token.
        :type request: Request
        :return: An HTTP response containing the serialized user data.
        :rtype: Response
        """
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    """
    API view for logging out a user.

    Handles POST requests to log out a user by deleting their authentication token.

    """

    def post(self, request):
        """
        Handle POST requests to log out a user.

        :param request: The incoming HTTP request containing the user token.
        :type request: Request
        :return: An HTTP response indicating the success or failure of the logout operation.
        :rtype: Response
        """
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterViewAPI(APIView):
    """
    API view for registering a new user.

    Handles POST requests to register a new user with admin privileges.

    """

    def post(self, request):
        """
        Handle POST requests to register a new user.

        :param request: The incoming HTTP request containing the admin token, username, and password.
        :type request: Request
        :return: An HTTP response indicating the success or failure of the registration.
        :rtype: Response
        """
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response(
            {'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)


class LoginView(CreateView):
    """
    View for handling user login.

    Inherits from CreateView to handle user login. Uses CustomUserCreationForm for customized user registration.

    """
    template_name = "authentication/login.html"
    form_class = CustomUserCreationForm
    model = User

    def post(self, request):
        """
        Handle POST requests to log in a user.

        :param request: The incoming HTTP request containing the username and password.
        :type request: Request
        :return: An HTTP response indicating the success or failure of the login operation.
        :rtype: HttpResponse
        """
        values = request.POST

        username = values['username']
        password1 = values['password1']

        user = authenticate(request, username=username, password=password1)

        response = redirect('/')

        if user is not None:
            login(request, user)
            userObject = User.objects.get(username=username)
            token, created = Token.objects.get_or_create(user=userObject)
            response.set_cookie(key='token', value=token)
        else:
            incorrect = ["This username or password do not exist"]
            template = loader.get_template("authentication/login.html")
            context = {"errors": incorrect}

            return HttpResponse(template.render(context, request))

        return response


class RegisterView(CreateView):
    """
    View for user registration.

    Inherits from CreateView to handle user registration. Uses CustomUserCreationForm for customized user registration.

    """
    template_name = "authentication/register.html"
    form_class = CustomUserCreationForm
    model = User

    def get_form(self, form_class=None):
        """
        Customize the form widget attributes.

        :param form_class: The form class.
        :type form_class: CustomUserCreationForm
        :return: The customized form.
        :rtype: CustomUserCreationForm
        """
        form = super(RegisterView, self).get_form()
        form.fields['username'].widget = forms.TextInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Less than 150 characters',
                'required': 'required'})
        form.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': '8 characters or more',
                'required': 'required'})
        form.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Confirm password',
                'required': 'required'})
        form.fields['first_name'].widget = forms.TextInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Alex',
                'required': 'required'})
        form.fields['last_name'].widget = forms.TextInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': 'Smith',
                'required': 'required'})
        form.fields['email'].widget = forms.EmailInput(
            attrs={
                'class': 'form-control mb-2',
                'placeholder': 'example@decide.com',
                'required': 'required'})

        return form

    def post(self, request):
        """
        Handle POST requests to register a new user.

        :param request: The incoming HTTP request containing user registration data.
        :type request: Request
        :return: An HTTP response indicating the success or failure of the registration.
        :rtype: HttpResponse
        """
        values = request.POST

        username = values['username']
        password1 = values['password1']
        password2 = values['password2']
        email = values['email']
        first_name = values['first_name']
        last_name = values['last_name']
        form = CustomUserCreationForm()

        errors = []

        if (form.clean_confirmation(password1, password2)):
            errors.append("Passwords must be the same")

        if (form.username_clean_lenght(username)):
            errors.append("This username is larger than 150 characters")

        if (form.username_clean_exits(username)):
            errors.append("This username has already taken")

        if (form.username_clean_pattern(username)):
            errors.append("This username not match with the pattern")

        if (form.email_clean(email)):
            errors.append("This email has already taken")

        if (form.clean_password_lenght(password1)):
            errors.append("This password must contain at least 8 characters")

        if (form.clean_password_common(password1)):
            errors.append("This password is a common password")

        if (form.clean_password_too_similar(
                password1, username, first_name, last_name)):
            errors.append("This password is too similar to your personal data")

        if (form.clean_password_numeric(password1)):
            errors.append("This password is numeric")

        if (len(errors) > 0):
            template = loader.get_template("authentication/register.html")
            context = {"errors": errors}

            return HttpResponse(template.render(context, request))
        else:
            try:
                user = User(username=username)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.set_password(password1)

                email = EmailMessage(
                    "Message from the app Decide",
                    "This is a confirmation message: the user with name {} and email {} has registered in the app Decide recently.".format(
                        user.first_name,
                        user.email),
                    "",
                    [
                        user.email],
                    reply_to=[email])

                email.send()
                user.save()
                token, _ = Token.objects.get_or_create(user=user)

            except IntegrityError:
                return HttpResponse(
                    "Integrity Error raised",
                    status=HTTP_400_BAD_REQUEST)

            return redirect('/')


def main(request):
    """
    Main view for handling authentication.

    :param request: The incoming HTTP request.
    :type request: Request
    :return: An HTTP response with the authentication template.
    :rtype: HttpResponse
    """
    template = loader.get_template("authentication/authentication.html")
    context = {}
    is_authenticated = False

    if request.user.is_authenticated:
        is_authenticated = True
        context['username'] = request.user.username

    context['authenticated'] = is_authenticated

    return HttpResponse(template.render(context, request))


def logout_view(request):
    """
    Logout view to handle user logout.

    :param request: The incoming HTTP request.
    :type request: Request
    :return: An HTTP response redirecting to the home page after logout.
    :rtype: HttpResponse
    """
    response = redirect('/')
    if request.user.is_authenticated:
        logout(request)
        response.delete_cookie('token')
        response.delete_cookie('decide')
    return response
