from rest_framework.views import APIView
from rest_framework.response import Response


class PostProcView(APIView):
    """
    API view for post-processing voting results.

    This view provides three types of post-processing:
    1. Identity: Keep the votes as is.
    2. Text: Post-processing for text-based voting.
    3. Weight: Post-processing considering weights for votes.

    :ivar int VOTES_WEIGHT: The default weight for votes.
    :cvar VOTES_WEIGHT: int

    :method identity: Post-process voting results with identity transformation.
    :method text: Post-process text-based voting results.
    :method weight: Post-process voting results considering weights.
    :method post: Handle POST requests for post-processing voting results.
    """

    def identity(self, options):
        """
        Post-process voting results with identity transformation.

        :param options: List of voting options.
        :type options: list
        :return: Response containing the post-processed results.
        :rtype: Response
        """
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            })

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)

    def text(self, text_votes):
        """
        Post-process text-based voting results.

        :param text_votes: List of text-based voting results.
        :type text_votes: list
        :return: Response containing the post-processed results.
        :rtype: Response
        """
        out = []

        for vote in text_votes:
            out.append({
                **vote,
                'postproc': vote['vote'],
            })

        return Response(out)

    def weight(self, options):
        """
        Post-process voting results considering weights.

        :param options: List of voting options with weights.
        :type options: list
        :return: Response containing the post-processed results.
        :rtype: Response
        """
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes_wights'],
            })

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)

    def post(self, request):
        """
        Handle POST requests for post-processing voting results.

        The expected request data includes:
        - 'type': IDENTITY | TEXT | WEIGHT
        - 'options': List of voting options.
        - 'text_votes': List of text-based voting results.

        :param request: The incoming HTTP request containing post-processing data.
        :type request: Request
        :return: Response containing the post-processed results.
        :rtype: Response
        """

        t = request.data.get('type', 'IDENTITY')
        opts = request.data.get('options', [])
        text_votes = request.data.get('text_votes', [])

        if t == 'IDENTITY':
            return self.identity(opts)

        if t == 'TEXT':
            return self.text(text_votes)

        if t == 'WEIGHT':
            return self.weight(opts)

        return Response({})
