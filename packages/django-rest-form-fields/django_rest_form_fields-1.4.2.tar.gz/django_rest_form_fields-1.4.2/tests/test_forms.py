from unittest import TestCase

from django.forms import CharField
from django.db import models
from django_rest_form_fields import RestCharField, RestChoiceField
from django_rest_form_fields.forms import BaseForm, BaseModelForm


class ModelExample(models.Model):
    model_field = models.CharField(max_length=255)


class SourceBaseFormTest(TestCase):
    data = {
        'src': 'test'
    }

    def _test_form(self, base_cls, fields, result):
        FormExample = type('FormExample', (base_cls,), fields)

        f = FormExample(self.data)
        f.full_clean()
        self.assertDictEqual(result, f.cleaned_data)

    def test_source(self):
        self._test_form(BaseForm, {'dest': RestCharField(source='src')}, {'dest': 'test'})

    def test_no_source(self):
        self._test_form(BaseForm, {'src': RestCharField()}, {'src': 'test'})

    def test_native_field(self):
        self._test_form(BaseForm, {'src': CharField()}, {'src': 'test'})

    def test_required(self):
        self._test_form(BaseForm, {'dest': RestCharField(source='absent', required=False)}, {'dest': None})
        self._test_form(BaseForm, {'dest': RestCharField(source='src', required=False)},
                        {'dest': 'test'})

    def test_initial(self):
        self._test_form(BaseForm, {'dest': RestCharField(source='absent', required=False, initial='init')},
                        {'dest': 'init'})
        self._test_form(BaseForm, {'dest': RestCharField(source='src', required=False, initial='init')},
                        {'dest': 'test'})

    def test_choice_field(self):
        # The was a bug in RestChoiceField due to duplicate init
        self._test_form(BaseForm, {'dest': RestChoiceField(source='src', choices=('test',))}, {'dest': 'test'})


class SourceBaseModelFormTest(TestCase):
    data = {
        'src': 'test',
        'model_field': 'm'
    }

    def _test_form(self, base_cls, fields, result):
        fields['Meta'] = type('Meta', (), {'model': ModelExample, 'fields': ('model_field',)})
        FormExample = type('FormExample', (base_cls,), fields)

        f = FormExample(self.data)
        f.full_clean()
        self.assertDictEqual(result, f.cleaned_data)

    def test_source(self):
        self._test_form(BaseModelForm, {'dest': RestCharField(source='src')}, {'dest': 'test', 'model_field': 'm'})

    def test_no_source(self):
        self._test_form(BaseModelForm, {'src': RestCharField()}, {'src': 'test', 'model_field': 'm'})

    def test_native_field(self):
        self._test_form(BaseModelForm, {'src': CharField()}, {'src': 'test', 'model_field': 'm'})

    def test_required(self):
        self._test_form(BaseModelForm, {'dest': RestCharField(source='absent', required=False)},
                        {'dest': None, 'model_field': 'm'})
        self._test_form(BaseModelForm, {'dest': RestCharField(source='src', required=False)},
                        {'dest': 'test', 'model_field': 'm'})

    def test_initial(self):
        self._test_form(BaseModelForm, {'dest': RestCharField(source='absent', required=False, initial='init')},
                        {'dest': 'init', 'model_field': 'm'})
        self._test_form(BaseModelForm, {'dest': RestCharField(source='src', required=False, initial='init')},
                        {'dest': 'test', 'model_field': 'm'})


class RequiredBaseModelFormTest(TestCase):
    def test_base_form(self):
        class TestForm(BaseForm):
            test = RestCharField(max_length=255, required=False)

        f = TestForm({})
        f.full_clean()
        self.assertTrue(f.is_valid())
        self.assertDictEqual({'test': None}, f.cleaned_data)

    def test_model_form(self):
        class TestForm(BaseModelForm):
            class Meta:
                model = ModelExample
                fields = ('model_field',)

            model_field = RestCharField(max_length=255, required=False)

        f = TestForm({})
        f.full_clean()
        self.assertTrue(f.is_valid())
        self.assertDictEqual({'model_field': None}, f.cleaned_data)

    def test_model_form_initial(self):
        class TestForm(BaseModelForm):
            class Meta:
                model = ModelExample
                fields = ('model_field',)

            model_field = RestCharField(max_length=255, required=False, initial='init')

        f = TestForm({})
        f.full_clean()
        self.assertTrue(f.is_valid())
        self.assertDictEqual({'model_field': 'init'}, f.cleaned_data)
