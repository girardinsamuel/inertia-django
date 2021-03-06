from unittest import TestCase
from unittest.mock import MagicMock
from unittest import mock
import django
from django.conf import settings
from django.test import RequestFactory
from django.http import HttpResponse
import os

settings.configure(
    VERSION=1, DEBUG=True,
    TEMPLATES= [{
         'BACKEND': 'django.template.backends.django.DjangoTemplates',
         'APP_DIRS': True,
         'DIRS': [ os.path.join('testutils'), ],
    }]
)
django.setup()
from inertia.version import asset_version
from inertia.views import render_inertia
from inertia.middleware import InertiaMiddleware


class TestInertia(TestCase):
    def test_views(self):
        requestfactory = RequestFactory()
        request = requestfactory.get("/")
        response = render_inertia(request, "Index")
        self.assertTrue(b'id="page"' in response.content)

    def set_session(self, request):
        dict_sessions = {
            'share': {}
        }
        request.session = MagicMock()
        request.session.__getitem__.side_effect = lambda key: dict_sessions[key]

    def test_simple_view(self):
        request = RequestFactory().get("/")
        self.set_session(request)
        response = InertiaMiddleware(lambda x: HttpResponse())(request)
        self.assertTrue(response.status_code==200, response.status_code)

    def test_middlware_missing_header(self):
        view = lambda x: HttpResponse()
        defaults = {
            'X-Inertia': 'true',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Inertia-Version': str(asset_version.get_version()+1),
        }
        request = RequestFactory().get("/")
        request.headers = defaults
        self.set_session(request)
        response = InertiaMiddleware(view)(request)
        self.assertTrue(response.status_code == 409, response.status_code)

    def test_middleware(self):
        view = lambda request: HttpResponse()
        defaults = {
            'x-Inertia': 'true',
            'X-Inertia-Version': asset_version.get_version(),
            'x-Requested-With': 'XMLHttpRequest'
        }
        request = RequestFactory().get("/", **defaults)
        request.headers = defaults
        self.set_session(request)
        response = InertiaMiddleware(view)(request)
        self.assertTrue(response.status_code == 200, response.status_code)
