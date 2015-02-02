#!/usr/bin/env python3

import os.path
import asyncio
from aiohttp import web


@asyncio.coroutine
def static_serve(request):
    match_path = request.match_info['all']
    found = os.path.join("public", match_path)

    serve = None

    if os.path.isfile(found):
        # found a file to serve
        serve = found
            
    elif os.path.isdir(found):
        # index special case
        redirect = not match_path.endswith("/")
        index_file = os.path.join(found, "index.html")
        if os.path.isfile(index_file):
            serve = index_file

    if serve:
        with open(serve, "rb") as response_file:
            return web.Response(
                body = response_file.read())

    else:
        return web.Response(text="404!")


def httpd(loop):
    """
    Serve content over http.
    """
    app = web.Application()
    app.router.add_route('GET', '/{all:.*}', static_serve)
    httpd = loop.create_server(app.make_handler(), '0.0.0.0', 8080)
    srv = loop.run_until_complete(httpd)
    print('serving on', srv.sockets[0].getsockname())
    

def main():
    loop = asyncio.get_event_loop()
    httpd(loop)

    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
