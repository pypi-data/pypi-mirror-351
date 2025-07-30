"""
This file contains extended BaseForm class
"""
from django import forms
from typing import Any


class SourceFormMixin(object):
    """
    Adds hooks that need to be called in order to process field's source attribute
    """
    def _post_init(self, *args, **kwargs):  # type: (*Any, **Any) -> None
        """
        Replace attribute names with source names if they exist and remember replaces
        :param args: Init arguments
        :param kwargs: Init kwargs
        :return: None
        """
        self._src_replaces = {}
        result_fields = {}
        for name, f in self.fields.items():  # noqa
            if getattr(f, 'source', None):
                self._src_replaces[f.source] = name
                result_fields[f.source] = f
            else:
                result_fields[name] = f

        self.fields = result_fields

    def _post_clean_fields(self):  # type: () -> None
        """
        Replace source field names with attribute names
        :return: None
        """
        self.cleaned_data = {self._src_replaces.get(name, name): val for name, val in self.cleaned_data.items()}  # noqa


class BaseForm(forms.Form, SourceFormMixin):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)

    def _clean_fields(self):
        super(BaseForm, self)._clean_fields()
        self._post_clean_fields()


class BaseModelForm(forms.ModelForm, SourceFormMixin):
    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)

    def _clean_fields(self):
        super(BaseModelForm, self)._clean_fields()
        self._post_clean_fields()
