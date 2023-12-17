import json

from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView

from base import mods
from census.models import Census
from store.models import Vote


class VisualizerView(TemplateView):
    template_name = 'visualizer/visualizer.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voting_id = kwargs.get('voting_id', 0)
    
        try:
            voting = mods.get('voting', params={'id': voting_id})
            context['voting'] = json.dumps(voting[0])
            num_census=0
            num_votes=0
            participation="-"

            if voting[0].get('start_date'):
                num_census = Census.objects.filter(voting_id=voting_id).count()
                num_votes = Vote.objects.filter(voting_id=voting_id).count()
                num_voters= len(set(vote.voter_id for vote in Vote.objects.filter(voting_id=voting_id)))
                if num_census != 0:
                    participation = str(round((num_voters*100)/num_census,2))+'%'

            realtimedata = {'num_census':num_census, 'num_votes':num_votes, 'participation':participation}
            context['realtimedata'] = realtimedata
            
        except:
            raise Http404
            
        return context