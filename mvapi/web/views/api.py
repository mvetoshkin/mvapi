from flask.views import View


class APIView(View):
    methods = ['get', 'post', 'patch', 'delete']

    def dispatch_request(self, **kwargs):
        return 'Hello, world!'
