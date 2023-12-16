

from django import forms
from .models import Census


class CreationCensusForm(forms.Form):
    voting_id = forms.IntegerField()
    voter_id = forms.IntegerField()


    class Meta: 
        model = Census
        fields = (
            'voting_id',
            'voter_id',
        )

    def save (self, commit = True):
        census = super(CreationCensusForm, self).save(commit = False)
        census.voting_id = self.cleaned_data['voting_id']
        census.voter_id = self.cleaned_data['voter_id']

        if commit : 
            census.save()
        return census





