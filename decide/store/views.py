from django.utils.dateparse import parse_datetime
import django_filters.rest_framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

from .models import Vote
from .serializers import VoteSerializer
from base.perms import UserIsStaff
from . import utils

VOTING_TYPES = {
    'preference': utils.classic_store,
    'yesno': utils.classic_store,
    'choices': utils.choices_store,
    'comment': utils.classic_store,
    'classic': utils.classic_store,
}


class StoreView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('voting_id', 'voter_id')

    def get(self, request):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        return super().get(request)

    def post(self, request):
        voting_type = request.data.get('voting_type')
        if voting_type not in VOTING_TYPES.keys():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        status_code = VOTING_TYPES[voting_type](request)
        return Response({}, status=status_code)
