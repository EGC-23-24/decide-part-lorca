from rest_framework.views import APIView
from rest_framework.response import Response


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            });

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)
    
    def text(self, text_votes):
        out = []

        for vote in text_votes:
            out.append({
                **vote,
                'postproc': vote['vote'],
            });

        return Response(out)
    
    def weight(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes_wights'],
            });

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)
    
    def post(self, request):
        """
         * type: IDENTITY | EQUALITY | WEIGHT
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
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
