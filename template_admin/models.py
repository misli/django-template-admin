# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.template import Template as DjangoTemplate, TemplateSyntaxError
from django.template.base import UNKNOWN_SOURCE, DebugLexer, Origin, Parser
from django.template.engine import Engine
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class Template(models.Model):
    template_name = models.CharField(
        _("template name"), editable=False, max_length=250, unique=True
    )
    enabled = models.BooleanField(_("enabled"), default=False)
    changed_content = models.TextField(
        _("changed content"), blank=True, default="", null=False
    )
    default_content = models.TextField(_("default content"), editable=False, null=True)
    original_default_content = models.TextField(
        _("original default content"), editable=False, null=True
    )
    default_content_changed = models.BooleanField(
        _("default content changed"), default=False, editable=False
    )
    last_modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = _("template")
        verbose_name_plural = _("templates")
        ordering = ("template_name",)

    def __str__(self):
        return "{}, {}".format(
            self.template_name,
            _("enabled") if self.enabled else _("disabled"),
        )

    def clean(self):
        template = DjangoTemplate("")
        template.source = self.changed_content
        try:
            engine = Engine.get_default()
            lexer = DebugLexer(self.changed_content)
            tokens = lexer.tokenize()
            parser = Parser(
                tokens,
                engine.template_libraries,
                engine.template_builtins,
                Origin(UNKNOWN_SOURCE),
            )
            parser.parse()
        except TemplateSyntaxError as e:
            exception_info = template.get_exception_info(e, e.token)
            raise ValidationError(
                {
                    "changed_content": mark_safe(
                        "{message}<br/>Line {line}:\n<pre>{before}<b>{during}</b>{after}</pre>".format(
                            **exception_info
                        )
                    )
                }
            ) from e
