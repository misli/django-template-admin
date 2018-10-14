# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Template(models.Model):
    template_name = models.CharField(_('template name'), editable=False, max_length=250, unique=True)
    enabled = models.BooleanField(_('enabled'), default=False)
    changed_content = models.TextField(_('changed content'), blank=True, default='', null=False)
    default_content = models.TextField(_('default content'), editable=False, null=True)
    original_default_content = models.TextField(_('original default content'), editable=False, null=True)
    default_content_changed = models.BooleanField(_('default content changed'), default=False, editable=False)
    last_modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('template_name',)

    def __str__(self):
        return '{}, {}'.format(
            self.template_name,
            _('enabled') if self.enabled else _('disabled'),
        )
