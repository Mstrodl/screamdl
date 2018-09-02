#!/usr/bin/env python3

import youtube_dl
import tornado.ioloop
import tornado.web
import urllib.error
import math
import re

ydl = youtube_dl.YoutubeDL({})

all_extractors = youtube_dl.list_extractors(math.inf)
supported = []
supported_re = []
bad_extractors = ["generic"]

for extractor in all_extractors:
    if extractor.IE_NAME in bad_extractors:
        continue
    if not isinstance(extractor, youtube_dl.extractor.common.SearchInfoExtractor):
        supported.append(extractor.IE_NAME)
        supported_re.append(extractor._VALID_URL)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        video_url = self.get_query_argument("v", default="")
        if not any([re.search(extractor_re, video_url) for extractor_re in supported_re]):
            self.set_status(415)
            return self.write({
                "message": "UNSUPPORTED_SITE",
                "supported": supported
            })
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
