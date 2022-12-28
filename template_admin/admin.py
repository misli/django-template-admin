from difflib import HtmlDiff

from django import forms
from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name", "enabled", "default_content_changed")
    list_filter = ("enabled", "default_content_changed")
    readonly_fields = (
        "default_content_readonly",
        "original_default_content_readonly",
        "changed_content_diff",
        "default_content_diff",
    )
    search_fields = (
        "template_name",
        "changed_content",
        "default_content",
        "original_default_content",
    )

    @property
    def media(self):
        return super(TemplateAdmin, self).media + forms.Media(
            css={"all": ("template_admin/htmldiff.css",)}
        )

    def save_model(self, request, obj, form, change):
        obj.original_default_content = obj.default_content if obj.enabled else None
        obj.default_content_changed = False
        obj.save()

    def default_content_readonly(self, obj):
        return mark_safe(
            '<textarea readonly rows="{}">{}</textarea>'.format(
                len(obj.default_content.splitlines()),
                escape(obj.default_content),
            )
        )

    default_content_readonly.short_description = _("default content")

    def original_default_content_readonly(self, obj):
        return mark_safe(
            '<textarea readonly rows="{}">{}</textarea>'.format(
                len(obj.original_default_content.splitlines()),
                escape(obj.original_default_content),
            )
        )

    original_default_content_readonly.short_description = _("original default content")

    def changed_content_diff(self, obj):
        return (
            mark_safe(
                HtmlDiff().make_table(
                    obj.default_content.splitlines(),
                    obj.changed_content.splitlines(),
                    fromdesc=_("default content"),
                    todesc=_("changed content"),
                )
            )
            if obj.changed_content
            else "-"
        )

    changed_content_diff.short_description = _(
        "difference between default and changed content"
    )

    def default_content_diff(self, obj):
        return (
            mark_safe(
                HtmlDiff().make_table(
                    obj.original_default_content.split("\n")[:-1],
                    obj.default_content.split("\n")[:-1],
                    fromdesc=_("original default content"),
                    todesc=_("current default content"),
                )
            )
            if obj.default_content_changed
            else "-"
        )

    default_content_diff.short_description = _(
        "difference between original and current default content"
    )
