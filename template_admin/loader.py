# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db.utils import IntegrityError, ProgrammingError
from django.template import Origin, Template, TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader
from django.utils import timezone

from .models import Template as TemplateModel

REFRESH_INTERVAL = getattr(settings, 'TEMPLATE_ADMIN_REFRESH_INTERVAL', 30)


class Loader(BaseLoader):
    supports_recursion = True

    def __init__(self, engine, loaders):
        self.last_checked = None
        self.loaders = engine.get_template_loaders(loaders)
        self.template_objects = {}
        super(Loader, self).__init__(engine)

    def get_template(self, template_name, skip=None, **kwargs):
        # find upstream template
        template = None
        tried = []
        for loader in self.loaders:
            try:
                template = loader.get_template(template_name, skip=skip, **kwargs)
                break
            except TemplateDoesNotExist as e:
                tried.extend(e.tried)

        origin = Origin(name=template_name, template_name=template_name, loader=self)

        if not skip:
            try:
                # refresh template objects cache
                now = timezone.now()
                if not self.last_checked or (now - self.last_checked).seconds >= REFRESH_INTERVAL:
                    filter_args = {'last_modified__gte': self.last_checked} if self.last_checked else {}
                    for template_obj in TemplateModel.objects.filter(**filter_args).iterator():
                        self.template_objects[template_obj.template_name] = template_obj
                    self.last_checked = now

                # create / update template object
                if template_name not in self.template_objects:
                    self.template_objects[template_name] = TemplateModel(template_name=template_name)
                template_obj = self.template_objects[template_name]
                default_content = template and template.source
                if template_obj.default_content != default_content or template_obj.pk is None:
                    template_obj.default_content = default_content
                    template_obj.default_content_changed = (
                        template_obj.original_default_content is not None and
                        template_obj.default_content != template_obj.original_default_content
                    )
                    template_obj.save()

                # use template with changed content
                if template_obj.enabled:
                    template = Template(template_obj.changed_content, origin, template_name, self.engine)
            except (IntegrityError, ProgrammingError):  # pragma: no cover
                # IntegrityError: already created in other thread
                # ProgrammingError: called before (or during) migration
                pass

        if template is None:
            raise TemplateDoesNotExist(template_name, tried=tried)

        return template
