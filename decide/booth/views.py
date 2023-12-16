import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from rest_framework.authtoken.models import Token

from base import mods


# TODO: check permissions and census
class BoothView(TemplateView):
    template_name = 'booth/booth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get('voting_id', 0)
        context['user'] = self.request.user
        if self.request.user.is_authenticated:
            token, created = Token.objects.get_or_create(user=self.request.user)
            context['token'] = token.key
        else:
            context['token'] = ''
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

        return context
