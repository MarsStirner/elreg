# -*- coding: utf-8 -*-

from django import forms
from livesettings.overrides import get_overrides
from livesettings.values import Value
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import livesettings.signals as signals
import settings
import os

NOTSET = object()

log = logging.getLogger('configuration')

class ImageValue(Value):

    class field(forms.ImageField):

        class FakeFieldFile(object):
            """
            Quacks like a FieldFile (has a .url and unicode representation), but
            doesn't require us to care about storages etc.

            """
            url = ''
            name = ''

            def __unicode__(self):
                return self.name

        def __init__(self, *args, **kwargs):
            kwargs['required'] = False
            if kwargs['initial']:
                if os.path.isfile(os.path.join(settings.MEDIA_ROOT, kwargs['initial'])):
                    file_obj = self.FakeFieldFile()
                    file_obj.name = kwargs['initial']
                    file_obj.url = os.path.join(settings.MEDIA_URL, kwargs['initial'])
                    kwargs['initial'] = file_obj

            forms.ImageField.__init__(self, *args, **kwargs)

    def update(self, value, request):
        use_db, overrides = get_overrides()
        if request.FILES:
            try:
                file = request.FILES["%s__%s" % (self.group.key,self.key)]
            except:
                pass
            else:
                value = self.__handle_uploaded_file(file)

        if use_db:
            current_value = self.value

            new_value = self.to_python(value)
            if current_value != new_value:
                if self.update_callback:
                    new_value = apply(self.update_callback, (current_value, new_value))

                db_value = self.get_db_prep_save(new_value)

                try:
                    s = self.setting
                    s.value = db_value

                except SettingNotSet:
                    s = self.make_setting(db_value)

                if self.use_default and self.to_python(self.default) == self.to_python(new_value):
                    if s.id:
                        log.info("Deleted setting %s.%s", self.group.key, self.key)
                        s.delete()
                else:
                    log.info("Updated setting %s.%s = %s", self.group.key, self.key, value)
                    s.save()

                signals.configuration_value_changed.send(self, old_value=current_value, new_value=new_value, setting=self)

                return True
        else:
            log.debug('not updating setting %s.%s - livesettings db is disabled',self.group.key, self.key)

        return False

    def to_python(self, value):
        if value == NOTSET:
            value = ""
        return unicode(value)

    def get_db_prep_save(self, value):
        "Returns a value suitable for storage into a CharField"
        if value == NOTSET:
            value = ""
        return unicode(value)

    def __handle_uploaded_file(self, file):
        try:
            default_storage.save(os.path.join(settings.MEDIA_ROOT, file.name), ContentFile(file.read()))
        except:
            return None
        else:
            return file.name

    def get_url(self):
        if self.value:
            return os.path.join(settings.MEDIA_URL, self.value)
        return ""


    to_editor = to_python