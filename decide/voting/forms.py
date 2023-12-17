from voting.models import Voting
from django.forms import ModelForm
from voting.filters import StartedFilter
from voting.models import Voting
from django.forms import ModelForm
from voting.filters import StartedFilter

    
class UpdateVotingForm(ModelForm):
    """
    A Django ModelForm for updating Voting instances.

    This form is used to update the details of a Voting instance. It includes fields for the name, description, and associated question of the Voting.

    Attributes:
        Meta: An inner class that provides metadata to the ModelForm class. It defines the model associated with the form and the fields to be included in the form.
    """
    
    class Meta:
        """
        Meta class for UpdateVotingForm.

        Specifies the model and fields associated with this form.

        Attributes:
            model: The model associated with this form.
            fields: The fields of the model to include in this form.
        """
        
        model = Voting
        fields = ['name', 'desc', 'question'] 
