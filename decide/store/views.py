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
    """
    API view for listing and creating votes.

    Inherits from Django Rest Framework's ListAPIView to provide a method for listing existing votes
    and a method for creating new votes based on the voting type.

    Attributes:
        queryset: A queryset that includes all Vote objects.
        serializer_class: Serializer class used to serialize Vote objects.
        filter_backends: Set of filter backends to be used for the queryset.
        filterset_fields: Fields of the Vote model that can be filtered.
    """

    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('voting_id', 'voter_id')

    def get(self, request):
        """
        Handles GET requests to retrieve a list of votes.

        Args:
            request: HttpRequest object.

        Returns:
            Response object containing serialized Vote data.

        Raises:
            PermissionDenied: If the user is not staff.
        """

        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        return super().get(request)

    def post(self, request):
        """
        Handles POST requests to create a new vote based on the voting type.

        Args:
            request: HttpRequest object containing voting_type and vote data.

        Returns:
            Response object with an HTTP status code.

        Raises:
            HTTP_400_BAD_REQUEST: If voting_type is not in the predefined voting types.
        """

        voting_type = request.data.get('voting_type')
        if voting_type not in VOTING_TYPES.keys():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        status_code = VOTING_TYPES[voting_type](request)
        return Response({}, status=status_code)
