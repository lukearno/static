from os import stat
from email.utils import formatdate
import time

from unittest import TestCase

from wsgi_intercept import http_client_intercept
import wsgi_intercept

try:
    import http.client as http_lib
except ImportError:
    import httplib as http_lib

import static


class StripAcceptEncoding(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        environ.pop('HTTP_ACCEPT_ENCODING', None)
        return self.application(environ, start_response)


class Intercepted(TestCase):

    def setUp(self):
        http_client_intercept.install()
        wsgi_intercept.add_wsgi_intercept('statictest', 80, self.get_app)

    def tearDown(self):
        wsgi_intercept.remove_wsgi_intercept('statictest', 80)
        http_client_intercept.uninstall()

    def assert_response(self, method, path, headers, status,
                        content=None, file_content=None,
                        response_headers=None):
        client = http_lib.HTTPConnection('statictest')
        client.request(method, path, headers=headers)
        response = client.getresponse()
        real_content = response.read()
        real_headers = dict(response.getheaders())
        self.assertEqual(response.status, status)
        if content is not None:
            self.assertEqual(real_content, content)
        if file_content is not None:
            with open(file_content, 'rb') as content_fp:
                content = content_fp.read()
            self.assertEqual(real_content, content)
        if response_headers is not None:
            for k, v in response_headers.items():
                if k not in real_headers:
                    k = k.lower()
                self.assertTrue(k in real_headers)
                self.assertEqual(real_headers[k], v)


class StaticClingWithIndexTests(Intercepted):

    def get_app(self):
        return static.Cling('tests/data/withindex')

    def test_client_can_get_a_static_file(self):
        self.assert_response(
            'GET', '/static.html', {},
            200,
            file_content='tests/data/withindex/static.html')

    def test_client_can_head_a_static_file(self):
        self.assert_response(
            'HEAD', '/static.html', {},
            200, b'')

    def test_client_gets_etag_and_last_modified_headers(self):
        file_path = 'tests/data/withindex/static.html'
        mtime = stat(file_path).st_mtime
        etag = str(mtime)
        last_modified = formatdate(mtime)
        self.assert_response(
            'GET', '/static.html', {},
            200,
            file_content=file_path,
            response_headers={'ETag': etag,
                              'Last-Modified': last_modified})

    def test_client_can_use_etags(self):
        file_path = 'tests/data/withindex/static.html'
        mtime = stat(file_path).st_mtime
        etag = str(mtime)
        self.assert_response(
            'GET', '/static.html', {'If-None-Match': etag},
            304, b'')

    def test_client_can_use_if_modified_since(self):
        modified_since = formatdate(time.time())
        self.assert_response(
            'GET', '/static.html',
            {'If-Modified-Since': modified_since},
            304, b'')

    def test_client_gets_index_file_if_path_is_ommitted(self):
        self.assert_response(
            'GET', '', {},
            200,
            file_content='tests/data/withindex/index.html')

    def test_client_gets_index_file_on_root(self):
        self.assert_response(
            'GET', '/', {},
            200,
            file_content='tests/data/withindex/index.html')

    def test_client_gets_index_file_on_subdirectory(self):
        self.assert_response(
            'GET', '/subdir/', {},
            200,
            file_content='tests/data/withindex/subdir/index.html')

    def test_client_gets_301_on_subdirectory_with_no_trailing_slash(self):
        self.assert_response(
            'GET', '/subdir?foo=1', {},
            301,
            response_headers={'Location': 'http://statictest/subdir/?foo=1'})

    def test_client_gets_a_405_on_POST(self):
        self.assert_response(
            'POST', '/static.html', {},
            405)

    def test_client_gets_a_405_on_PUT(self):
        self.assert_response(
            'POST', '/static.html', {},
            405)

    def test_client_gets_a_405_on_DELETE(self):
        self.assert_response(
            'POST', '/static.html', {},
            405)

    def test_client_cant_get_a_static_file_not_in_exposed_directory(self):
        self.assert_response(
            'GET', '../__init__.py', {},
            404)

    def test_client_gets_a_404_for_a_missing_file(self):
        self.assert_response(
            'GET', '/no-such-file.txt', {},
            404)


class StaticClingWithNoIndexTests(Intercepted):

    def get_app(self):
        return static.Cling('tests/data/noindex')

    def test_client_can_get_a_static_file(self):
        self.assert_response(
            'GET', '/static.html', {},
            200,
            file_content='tests/data/noindex/static.html')

    def test_client_gets_a_404_if_path_is_ommitted(self):
        self.assert_response(
            'GET', '', {},
            404)

    def test_client_gets_a_404_on_root(self):
        self.assert_response(
            'GET', '/', {},
            404)


class StaticShockTests(Intercepted):

    def get_app(self):
        return static.Shock(
            'tests/data/templates',
            (static.StringMagic(variables={'name': "Hamm"}),
             static.MoustacheMagic(variables={'color': "blue"})))

    def test_client_can_get_stp_without_extension(self):
        self.assert_response(
            'GET', '/index.html', {},
            200,
            b"Hello Hamm",
            response_headers={'Content-Type': 'text/html'})

    def test_client_can_get_stp_with_extension(self):
        self.assert_response(
            'GET', '/index.html.stp', {},
            200,
            b"Hello Hamm",
            response_headers={'Content-Type': 'text/html'})

    def test_client_gets_right_content_type_without_extension(self):
        self.assert_response(
            'GET', '/foo.css', {},
            200,
            b"body { color: blue; }",
            response_headers={'Content-Type': 'text/css'})

    def test_client_gets_right_content_type_with_extension(self):
        self.assert_response(
            'GET', '/foo.css.mst', {},
            200,
            b"body { color: blue; }",
            response_headers={'Content-Type': 'text/css'})

    def test_client_can_get_a_static_file_where_there_is_no_template(self):
        self.assert_response(
            'GET', '/static.txt', {},
            200,
            file_content="tests/data/templates/static.txt",
            response_headers={'Content-Type': 'text/plain'})

    def test_client_gets_a_404_for_a_missing_file(self):
        self.assert_response(
            'GET', '/no-such-file.txt', {},
            404)


class StaticClingWithPrezipping(Intercepted):

    def setUp(self):
        self._app = static.Cling('tests/data/prezip')
        super(StaticClingWithPrezipping, self).setUp()

    def get_app(self):
        return self._app

    def test_client_gets_prezipped_content(self):
        self.assert_response(
            'GET', '/static.txt', {'Accept-Encoding': 'gzip, deflate'},
            200,
            response_headers={'Content-Encoding': 'gzip'},
            file_content="tests/data/prezip/static.txt.gz")

    def test_client_gets_non_prezipped_when_no_accept_encoding_present(self):
        # strip HTTP_ACCEPT_ENCODING from the environ, to simulate not getting the header at all
        self._app = StripAcceptEncoding(self.get_app())
        self.assert_response(
            'GET', '/static.txt', {},
            200,
            file_content="tests/data/prezip/static.txt")

    def test_client_gets_non_prezipped_when_accept_missing_gzip(self):
        self.assert_response(
            'GET', '/static.txt', {},
            200,
            file_content="tests/data/prezip/static.txt")

    def test_client_gets_non_prezipped_when_prezipped_file_not_exist(self):
        self.assert_response(
            'GET', '/nogzipversionpresent.txt',
            {'Accept-Encoding': 'gzip, deflate'},
            200,
            file_content="tests/data/prezip/nogzipversionpresent.txt")
