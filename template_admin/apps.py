# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TemplateAdminConfig(AppConfig):
    name = 'template_admin'
    verbose_name = _('Template Administration')
