


class Request:
    def __init__(self, method, url, headers, body=''):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def __str__(self):
        return f"Request(method={self.method}, url={self.url}, headers={self.headers}, body={self.body})"


class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def __str__(self):
        return f"Response(status={self.status}, headers={self.headers}, body={self.body})"


class DefaultHook:

    def before_request(self, request: Request, **kwargs):
        #print("before_request")
        request.headers['Project-Id'] = kwargs.get("project_id")

    def after_response(self, request: Request, response: Response, **kwargs):
        #print("after_response")
        pass

    def on_error(self, error: Exception, request: Request, response: Response, **kwargs):
        #print("on_error")
        pass
