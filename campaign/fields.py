from django.conf import settings
from django.db import models
from django import forms
try:
    from django.utils import simplejson
except ImportError:
    import json as simplejson


class JSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None):
        if not isinstance(value, basestring):
            value = simplejson.dumps(value, indent=2)
        return super(JSONWidget, self).render(name, value, attrs)

class JSONFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = JSONWidget
        super(JSONFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value: return
        try:
            return simplejson.loads(value)
        except Exception as exc:
            raise forms.ValidationError(u'JSON decode error: %s' % (unicode(exc),))

class JSONField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        return super(JSONField, self).formfield(form_class=JSONFormField, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring):
            value = simplejson.loads(value)
        return value

    def get_db_prep_save(self, value, connection=None):
        if value is None: return
        return simplejson.dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^campaign\.fields\.JSONField"])
