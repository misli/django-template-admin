django-template-admin
=====================

Django application for advanced template management

Allows staff member (with corresponding permissions) to:

* list all templates used in the project and examine their content
* change the content of any template
* create new templates
* **see the differences** between the default content (from filesystem or other loader) and the changed content
* **see if the original content has changed** since the last change

Installation
------------

Install ``django-template-admin`` either from source or using pip.

Configuration
-------------
Add ``'template_admin'`` to ``settings.INSTALLED_APPS``.

Configure template loaders::

    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('template_admin.loader.Loader', [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ]),
    ]
