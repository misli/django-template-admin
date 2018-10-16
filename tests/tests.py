from __future__ import absolute_import

import os
import time

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.template import TemplateDoesNotExist, engines
from django.template.loader import get_template
from django.test import RequestFactory, TestCase

from template_admin import loader
from template_admin.models import Template


class TemplateLoaderTests(TestCase):

    def __init__(self, *args, **kwargs):
        super(TemplateLoaderTests, self).__init__(*args, **kwargs)

        # get default template content
        self.test_template_content = open(
            os.path.join(settings.BASE_DIR, 'tests', 'templates', 'template.html')
        ).read()

        # prepare changed template content
        self.test_template_changed_content = self.test_template_content.replace('h1', 'h2')

        # get template loader instance
        self.loader = engines.all()[0].engine.template_loaders[0]

    def setUp(self):
        # reset loader's cache
        self.loader.template_objects = {}

    def test_existing_template(self):
        loader.REFRESH_INTERVAL = 0

        # get_template returns default content
        self.assertEqual(
            get_template('template.html').template.source,
            self.test_template_content,
        )

        # get template from database
        template = Template.objects.get(template_name='template.html')

        # template is disabled by default
        self.assertFalse(template.enabled)

        # template contains default content
        self.assertEqual(
            template.default_content,
            self.test_template_content,
        )

        # add changed content to database
        template.changed_content = self.test_template_changed_content
        template.enabled = True
        template.save()

        # get_template returns changed content
        self.assertEqual(
            get_template('template.html').template.source,
            self.test_template_changed_content,
        )

        # disable template in database
        template.enabled = False
        template.save()

        # get_template returns default content again
        self.assertEqual(
            get_template('template.html').template.source,
            self.test_template_content,
        )

    def test_refresh_interval(self):
        loader.REFRESH_INTERVAL = 3

        # get_template returns default content
        self.assertEqual(
            get_template('template.html').template.source,
            self.test_template_content,
        )

        # get template from database
        template = Template.objects.get(template_name='template.html')

        # add changed content to database
        template.changed_content = self.test_template_changed_content
        template.enabled = True
        template.save()

        # get_template still returns default content
        self.assertEqual(
            get_template('template.html').template.source,
            self.test_template_content,
        )

        # sleep a while
        time.sleep(loader.REFRESH_INTERVAL)

        # get_template returns changed content
        self.assertEqual(
            get_template('template.html').template.source,
            self.test_template_changed_content,
        )

    def test_new_template(self):
        loader.REFRESH_INTERVAL = 0

        # template does not exist
        self.assertRaises(
            TemplateDoesNotExist,
            lambda: get_template('new.html'),
        )

        # create new template in database
        template = Template.objects.get(template_name='new.html')
        template.changed_content = self.test_template_changed_content
        template.enabled = True
        template.save()

        # check template's string representation
        self.assertEqual(str(template), 'new.html, enabled')

        # get_template returns changed content
        self.assertEqual(
            get_template('new.html').template.source,
            self.test_template_changed_content,
        )

        # disable template in database
        template.enabled = False
        template.save()

        # check template's string representation
        self.assertEqual(str(template), 'new.html, disabled')

        # template again does not exist
        self.assertRaises(
            TemplateDoesNotExist,
            lambda: get_template('new.html'),
        )


class TemplateAdminTests(TestCase):

    def __init__(self, *args, **kwargs):
        super(TemplateAdminTests, self).__init__(*args, **kwargs)

        # get template loader instance
        self.loader = engines.all()[0].engine.template_loaders[0]

    def setUp(self):
        # prepare request object
        self.request = RequestFactory().get('/')
        self.request.user = User.objects.create_user(
            username='admin',
            is_superuser=True,
        )
        self.request.session = {}

        # get TemplateAdmin instance
        self.template_admin = admin.site._registry[Template]

        # reset loader's cache
        self.loader.template_objects = {}

        # ensure some template in database
        get_template('template.html')

    def test_changelist_view(self):
        # get response from TemplateAdmin.changelist_view
        response = self.template_admin.changelist_view(self.request).render()

        # check response code
        self.assertEqual(response.status_code, 200)

    def test_change_view(self):
        # get template from database
        template = Template.objects.first()

        # get response from TemplateAdmin.change_view
        response = self.template_admin.change_view(self.request, str(template.id)).render()

        # check response code
        self.assertEqual(response.status_code, 200)

    def test_save_model(self):
        # get template from database
        template = Template.objects.first()

        # enable template
        template.enabled = True
        self.template_admin.save_model(self.request, template, None, True)

        # template has original default content equal to default content
        self.assertEqual(template.original_default_content, template.default_content)

        # disable template
        template.enabled = False
        self.template_admin.save_model(self.request, template, None, True)

        # ensure template has no original default content
        self.assertEqual(template.original_default_content, None)
