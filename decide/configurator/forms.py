from django import forms
from django.conf import settings
from django.utils import timezone
from voting.models import Voting, Question, QuestionOption, QuestionOptionRanked
from base.models import Auth


class ClassicForm(forms.ModelForm):
    question_desc = forms.CharField(label="Question")
    future_stop = forms.DateTimeField(
        label="Optionally, set an end date",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
    )
    option1 = forms.CharField(label="Option 1")
    option2 = forms.CharField(label="Option 2")
    more_options = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Voting
        fields = ["name", "desc", "future_stop"]

    def save(self):
        # Create Question
        question = create_question(self, "C")

        # Create Options for the Question
        option1 = self.cleaned_data["option1"]
        option2 = self.cleaned_data["option2"]
        QuestionOption(question=question, option=option1).save()
        QuestionOption(question=question, option=option2).save()
        if self.cleaned_data["more_options"]:
            more_options = self.cleaned_data["more_options"].split("\n")
            for option in more_options:
                QuestionOption(question=question, option=option).save()

        # Create Voting
        voting = create_voting(self, question)

        return voting

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["desc"].widget.attrs.update(
            {"class": "form-control", "rows": 3})
        self.fields["question_desc"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["future_stop"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["option1"].widget.attrs.update({"class": "form-control"})
        self.fields["option2"].widget.attrs.update({"class": "form-control"})
        self.fields["more_options"].widget.attrs.update(
            {"class": "form-control", "id": "id_options"}
        )


class YesNoForm(forms.ModelForm):
    question_desc = forms.CharField(label="Question")
    future_stop = forms.DateTimeField(
        label="Optionally, set an end date",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
    )

    class Meta:
        model = Voting
        fields = ["name", "desc", "future_stop"]

    def save(self):
        # Create Question
        question = create_question(self, "Y")

        # Create Voting
        voting = create_voting(self, question)

        return voting

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["desc"].widget.attrs.update(
            {"class": "form-control", "rows": 3})
        self.fields["question_desc"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["future_stop"].widget.attrs.update(
            {"class": "form-control"})


class MultipleChoiceForm(forms.ModelForm):
    question_desc = forms.CharField(label="Question")
    future_stop = forms.DateTimeField(
        label="Optionally, set an end date",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
    )
    option1 = forms.CharField(label="Option 1")
    option2 = forms.CharField(label="Option 2")
    more_options = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Voting
        fields = ["name", "desc", "future_stop"]

    def save(self):
        # Create Question
        question = create_question(self, "M")

        # Create Options for the Question
        option1 = self.cleaned_data["option1"]
        option2 = self.cleaned_data["option2"]
        QuestionOption(question=question, option=option1).save()
        QuestionOption(question=question, option=option2).save()
        if self.cleaned_data["more_options"]:
            more_options = self.cleaned_data["more_options"].split("\n")
            for option in more_options:
                QuestionOption(question=question, option=option).save()

        # Create Voting
        voting = create_voting(self, question)

        return voting

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["desc"].widget.attrs.update(
            {"class": "form-control", "rows": 3})
        self.fields["question_desc"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["future_stop"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["option1"].widget.attrs.update({"class": "form-control"})
        self.fields["option2"].widget.attrs.update({"class": "form-control"})
        self.fields["more_options"].widget.attrs.update(
            {"class": "form-control", "id": "id_options"}
        )


class PreferenceForm(forms.ModelForm):
    question_desc = forms.CharField(label="Question")
    future_stop = forms.DateTimeField(
        label="Optionally, set an end date",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
    )
    option1 = forms.CharField(label="Option 1")
    option2 = forms.CharField(label="Option 2")
    more_options = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Voting
        fields = ["name", "desc", "future_stop"]

    def save(self):
        # Create Question
        question = create_question(self, "R")

        # Create Options for the Question
        option1 = self.cleaned_data["option1"]
        option2 = self.cleaned_data["option2"]
        QuestionOptionRanked(question=question, option=option1).save()
        QuestionOptionRanked(question=question, option=option2).save()
        if self.cleaned_data["more_options"]:
            more_options = self.cleaned_data["more_options"].split("\n")
            for option in more_options:
                QuestionOptionRanked(question=question, option=option).save()

        # Create Voting
        voting = create_voting(self, question)

        return voting

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["desc"].widget.attrs.update(
            {"class": "form-control", "rows": 3})
        self.fields["question_desc"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["future_stop"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["option1"].widget.attrs.update({"class": "form-control"})
        self.fields["option2"].widget.attrs.update({"class": "form-control"})
        self.fields["more_options"].widget.attrs.update(
            {"class": "form-control", "id": "id_options"}
        )


class OpenQuestionForm(forms.ModelForm):
    question_desc = forms.CharField(label="Question")
    future_stop = forms.DateTimeField(
        label="Optionally, set an end date",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        required=False,
    )

    class Meta:
        model = Voting
        fields = ["name", "desc", "future_stop"]

    def save(self):
        # Create Question
        question = create_question(self, "T")

        # Create Voting
        voting = create_voting(self, question)

        return voting

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["desc"].widget.attrs.update(
            {"class": "form-control", "rows": 3})
        self.fields["question_desc"].widget.attrs.update(
            {"class": "form-control"})
        self.fields["future_stop"].widget.attrs.update(
            {"class": "form-control"})


def create_question(self, type):
    question_desc = self.cleaned_data["question_desc"]
    question = Question(desc=question_desc, type=type)
    question.save()
    return question


def create_auth():
    if not Auth.objects.filter(url=settings.BASEURL).exists():
        auth = Auth(name="Auth", url=settings.BASEURL)
        auth.save()
    else:
        auth = Auth.objects.filter(url=settings.BASEURL).first()
    return auth


def create_voting(self, question):
    # Create Auth
    auth = create_auth()

    # Create Voting
    voting = Voting(
        name=self.cleaned_data["name"],
        desc=self.cleaned_data["desc"],
        future_stop=self.cleaned_data["future_stop"],
        question=question,
        start_date=timezone.now(),
    )
    voting.save()
    voting.auths.add(auth)
    voting.create_pubkey()
    voting.save()
    return voting
