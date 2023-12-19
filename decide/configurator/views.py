from typing import Any
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from .forms import (
    ClassicForm,
    YesNoForm,
    MultipleChoiceForm,
    PreferenceForm,
    OpenQuestionForm,
)
from voting.models import Voting


def is_admin(user):
    return user.is_authenticated and user.is_staff


def configurator(request):
    if not is_admin(request.user):
        messages.error(request, "You must be an admin to access this page!")
        return HttpResponseRedirect("/")
    return render(request, "configurator/configurator.html")


class CreateClassicView(TemplateView):
    template_name = "configurator/create_classic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ClassicForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ClassicForm(request.POST)
        if form.is_valid():
            new_voting = form.save()
            request.session["voting_id"] = new_voting.id
            messages.success(request, "Classic voting created successfully!")
            return redirect(reverse("manage_census"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "You must be an admin to access this page!")
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)


class CreateYesNoView(TemplateView):
    template_name = "configurator/create_yes_no.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = YesNoForm()
        return context

    def post(self, request, *args, **kwargs):
        form = YesNoForm(request.POST)
        if form.is_valid():
            new_voting = form.save()
            request.session["voting_id"] = new_voting.id
            messages.success(request, "Yes/No voting created successfully!")
            return redirect(reverse("manage_census"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "You must be an admin to access this page!")
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)


class CreateMultipleChoiceView(TemplateView):
    template_name = "configurator/create_multiple_choice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = MultipleChoiceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = MultipleChoiceForm(request.POST)
        if form.is_valid():
            new_voting = form.save()
            request.session["voting_id"] = new_voting.id
            messages.success(
                request, "Multiple choice voting created successfully!")
            return redirect(reverse("manage_census"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "You must be an admin to access this page!")
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)


class CreatePreferenceView(TemplateView):
    template_name = "configurator/create_preference.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PreferenceForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PreferenceForm(request.POST)
        if form.is_valid():
            new_voting = form.save()
            request.session["voting_id"] = new_voting.id
            messages.success(
                request, "Preference voting created successfully!")
            return redirect(reverse("manage_census"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "You must be an admin to access this page!")
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)


class CreateOpenQuestionView(TemplateView):
    template_name = "configurator/create_open_question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = OpenQuestionForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OpenQuestionForm(request.POST)
        if form.is_valid():
            new_voting = form.save()
            request.session["voting_id"] = new_voting.id
            messages.success(
                request, "Open question voting created successfully!")
            return redirect(reverse("manage_census"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "You must be an admin to access this page!")
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)


class ManageCensusView(TemplateView):
    template_name = "configurator/manage_census.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voting_id = self.request.session.get("voting_id")
        context["voting"] = Voting.objects.get(id=voting_id)
        return context

    def dispatch(self, request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(
                request, "You must be an admin to access this page!")
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)
