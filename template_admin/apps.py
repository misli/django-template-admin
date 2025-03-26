from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TemplateAdminConfig(AppConfig):
    name = "template_admin"
    verbose_name = _("Template Administration")
