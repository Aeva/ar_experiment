#!/usr/bin/env python3

import os.path
import asyncio
import asyncio.subprocess
from aiohttp import web
from sh import pwgen, x11vnc
import window_query


@asyncio.coroutine
def vnc_subproc(window, password, port):
    cmd = ["x11vnc",
           "-id", window.window_id,
           "-localhost",
           "-passwd", password,
           "-httpport", str(port)]

    print("serving vnc on (localhost, {0}) : {1} : {2}".format(
        port, password, window.title))

    create = asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    proc = yield from create
    print("DEBUG: seems to block after this point :/")
    yield from proc.wait()
    print("vnc process closed")


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
    # create the evnet loop
    loop = asyncio.get_event_loop()

    # start up the http server
    httpd(loop)

    # start up vnc servers for each window
    vnc_servers = {}
    last_port = 14900
    for window in window_query.get_open_windows():
        password = pwgen(8, 1).strip()
        last_port = port = last_port + 1
        loop.run_until_complete(vnc_subproc(window, password, port))
        print("DEBUG: never reached")
        vnc_servers[window.window_id] = {
            "password" : password,
            "info" : window,
            "port" : port,
        }

    # start up tcp listeners for each vnc server
    

    # enter the event loop
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
