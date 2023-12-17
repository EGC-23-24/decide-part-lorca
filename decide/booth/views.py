import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404

from base import mods


# TODO: check permissions and census
class BoothView(TemplateView):
    """
    View for rendering the booth template with voting information.

    This view retrieves voting information based on the provided 'voting_id' parameter
    and renders the 'booth/booth.html' template with the voting details.

    :ivar template_name: The name of the HTML template to be rendered.
    :vartype template_name: str
    """
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the template.

        Retrieves voting information based on the 'voting_id' parameter and prepares
        the context data to be used in the template.

        :param kwargs: Keyword arguments passed to the view.
        :type kwargs: dict
        :return: A dictionary containing the context data.
        :rtype: dict
        :raises Http404: If there is an issue retrieving voting information.
        """
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)

        try:
            r = mods.get('voting', params={'id': vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]['pub_key'].items():
                r[0]['pub_key'][k] = str(v)

            context['voting'] = json.dumps(r[0])
        except:
            raise Http404

        context['KEYBITS'] = settings.KEYBITS

        if r[0]['question']['type'] == 'R':
            maxNumberOption = len(r[0]['question']['options'])
            context['maxOption'] = maxNumberOption
        else:
            context['maxOption'] = 0

        return context
