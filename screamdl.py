#!/usr/bin/env python3

import youtube_dl
import tornado.ioloop
import tornado.web
import urllib.error

ydl = youtube_dl.YoutubeDL({})

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        video_url = self.get_query_argument("v", default="")
        with ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                return self.write(info)
            except youtube_dl.utils.DownloadError as err:
                exception = err.exc_info[1]
                if isinstance(exception, urllib.error.HTTPError):
                    self.set_status(exception.code)
                elif isinstance(exception, youtube_dl.utils.ExtractorError):
                    self.set_status(500)
                else:
                    self.set_status(500)
                return self.write(str(exception))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
