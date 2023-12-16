from voting.models import Voting
from django.forms import ModelForm
from voting.filters import StartedFilter
from voting.models import Voting
from django.forms import ModelForm
from voting.filters import StartedFilter

    
class UpdateVotingForm(ModelForm):
    class Meta:
        model = Voting
        fields = ['name', 'desc', 'question'] 
