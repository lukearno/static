import sys

from static import Cling


def run():
    host, port, directory = sys.argv[1:4]
    app = Cling(directory)
    try:
        from wsgiref.simple_server import make_server
        make_server(host, int(port), app).serve_forever()
    except KeyboardInterrupt:
        print("Cio, baby!")
