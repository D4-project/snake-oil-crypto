import tornado

class JSONHandler(tornado.web.RequestHandler):
    def set_default_headers(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json")