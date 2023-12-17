

from django import forms
from .models import Census


class CreationCensusForm(forms.Form):
    """
    A Django form for creating Census instances.

    This form allows for the creation of new Census records, associating a voter with a voting.

    Attributes:
        voting_id (forms.IntegerField): Field for the ID of the voting.
        voter_id (forms.IntegerField): Field for the ID of the voter.

    Inner class:
        Meta: Provides metadata for the form, including model association and fields.
    """
    
    voting_id = forms.IntegerField()
    voter_id = forms.IntegerField()


    class Meta: 
        """
        Meta class for CreationCensusForm.

        Specifies the model and fields associated with this form.

        Attributes:
            model: The model associated with this form.
            fields: The fields of the model to include in this form.
        """
        
        model = Census
        fields = (
            'voting_id',
            'voter_id',
        )

    def save (self, commit = True):
        """
        Saves the form instance as a Census model instance.

        Overrides the save method to handle the saving of the Census instance with the provided 'voting_id' and 'voter_id'.

        :param commit: Whether to save the instance to the database. Defaults to True.
        :type commit: bool
        :return: The saved or unsaved Census instance, depending on the commit parameter.
        :rtype: Census
        """
        
        census = super(CreationCensusForm, self).save(commit = False)
        census.voting_id = self.cleaned_data['voting_id']
        census.voter_id = self.cleaned_data['voter_id']

        if commit : 
            census.save()
        return census





