import json

from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView

from base import mods
from census.models import Census
from store.models import Vote


class VisualizerView(TemplateView):
    """
    View for visualizing voting data.

    This view renders a template for visualizing voting statistics, including the number of census entries,
    votes, and participation rate.

    :ivar template_name: The name of the template to render.
    :vartype template_name: str
    """
    template_name = 'visualizer/visualizer.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve the context data for rendering the template.

        Retrieves information about a specific voting instance, including the number of census entries,
        votes, and participation rate.

        :param kwargs: Keyword arguments.
        :type kwargs: dict
        :return: A dictionary containing context data for the template.
        :rtype: dict
        :raises Http404: If an error occurs while retrieving or processing the voting data.
        """
        context = super().get_context_data(**kwargs)
        voting_id = kwargs.get('voting_id', 0)

        try:
            voting = mods.get('voting', params={'id': voting_id})
            context['voting'] = json.dumps(voting[0])
            num_census = 0
            num_votes = 0
            participation = "-"

            if voting[0].get('start_date'):
                num_census = Census.objects.filter(voting_id=voting_id).count()
                num_votes = Vote.objects.filter(voting_id=voting_id).count()
                num_voters = len(
                    set(vote.voter_id for vote in Vote.objects.filter(voting_id=voting_id)))
                if num_census != 0:
                    participation = str(
                        round(
                            (num_voters * 100) / num_census,
                            2)) + '%'

            realtimedata = {
                'num_census': num_census,
                'num_votes': num_votes,
                'participation': participation}
            context['realtimedata'] = realtimedata

        except BaseException:
            raise Http404

        return context
