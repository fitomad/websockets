from tornado import web

class AppStaticFileHandler(web.StaticFileHandler):
    #
    # Para evitar que los archivos estaticos
    # permanezcan en cache
    #
    def set_extra_headers(self, path):
        self.set_header('Cache-control', 'no-store, no-cache, must-revalidate, max-age=0')