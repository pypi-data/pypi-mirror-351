"""
This file contains tests for fields.py
"""

import datetime
import json
import random
import re
import uuid
from datetime import timezone, date
from io import BytesIO
from unittest import TestCase

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.forms import Form
from django.test import override_settings
from django.utils.timezone import now

from django_rest_form_fields.compatibility import to_timestamp
from django_rest_form_fields.fields import RestBooleanField, LowerCaseEmailField, TimestampField, DateUnitField, \
    ColorField, IdArrayField, IdSetField, TruncatedCharField, JsonField, ArrayField, UrlField, RestCharField, \
    RestChoiceField, RestIntegerField, RegexField, UUIDField, DateTimeField, MonthField, FileField, RestFloatField, \
    DateField, IdField


class TestErrorValidator(BaseValidator):
    """
    I use this validator to raise error in run_validators for test purposes
    """
    compare = lambda self, a, b: True  # noqa: E731
    clean = lambda self, x: 0  # noqa: E731
    message = "This validator always raises error, if run_validators is run"
    code = 'always_error'


class LowerCaseEmailFieldTest(TestCase):
    def test_to_lower(self):
        f = LowerCaseEmailField()
        self.assertEqual(f.clean('TeSt@mail.ru'), 'test@mail.ru')

    def test_required(self):
        f = LowerCaseEmailField(required=False)
        self.assertEqual(None, f.clean(None))

        f = LowerCaseEmailField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        f = LowerCaseEmailField(required=False, initial='test@mail.ru')
        self.assertEqual('test@mail.ru', f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = LowerCaseEmailField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class RestBooleanFieldTest(TestCase):
    def test_true(self):
        f = RestBooleanField()
        self.assertEqual(True, f.clean('true'))

    def test_1(self):
        f = RestBooleanField()
        self.assertEqual(True, f.clean('1'))

    def test_1_in_form(self):
        # Here django NullBooleanSelect.value_from_datadict is called, causing "1" to be evaluated as False...
        class TestForm(Form):
            b = RestBooleanField()

        f = TestForm({"b": "1"})

        self.assertTrue(f.is_valid())
        self.assertEqual({"b": True}, f.cleaned_data)

    def test_false(self):
        f = RestBooleanField()
        self.assertEqual(False, f.clean('false'))

    def test_0(self):
        f = RestBooleanField()
        self.assertEqual(False, f.clean('0'))

    def test_empty_string(self):
        f = RestBooleanField()
        self.assertEqual(False, f.clean(''))

    def test_not_empty_string(self):
        f = RestBooleanField()
        self.assertEqual(True, f.clean('some_text'))

    def test_None(self):
        f = RestBooleanField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_not_required_true(self):
        f = RestBooleanField(required=False)
        self.assertEqual(True, f.clean('true'))

    def test_not_required_1(self):
        f = RestBooleanField(required=False)
        self.assertEqual(True, f.clean('1'))

    def test_not_required_false(self):
        f = RestBooleanField(required=False)
        self.assertEqual(False, f.clean('false'))

    def test_not_required_0(self):
        f = RestBooleanField(required=False)
        self.assertEqual(False, f.clean('0'))

    def test_not_required_empty_string(self):
        f = RestBooleanField(required=False)
        self.assertEqual(False, f.clean(''))

    def test_not_required_not_empty_string(self):
        f = RestBooleanField(required=False)
        self.assertEqual(True, f.clean('some_text'))

    def test_not_required_None(self):
        f = RestBooleanField(required=False)
        self.assertEqual(None, f.clean(None))

    def test_initial_true(self):
        f = RestBooleanField(required=False, initial=True)
        self.assertEqual(True, f.clean(None))

    def test_initial_false(self):
        f = RestBooleanField(required=False, initial=False)
        self.assertEqual(False, f.clean(None))

    def test_required(self):
        f = RestBooleanField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = RestBooleanField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class RestIntegerFieldTest(TestCase):
    def test_correct(self):
        f = RestIntegerField()
        self.assertEqual(1, f.clean(1))
        f = RestIntegerField()
        self.assertEqual(123, f.clean(123))
        f = RestIntegerField()
        self.assertEqual(0, f.clean(0))
        f = RestIntegerField()
        self.assertEqual(-10, f.clean(-10))
        f = RestIntegerField()
        self.assertEqual(1, f.clean('1'))
        f = RestIntegerField()
        self.assertEqual(123, f.clean('123'))
        f = RestIntegerField()
        self.assertEqual(0, f.clean('0'))
        f = RestIntegerField()
        self.assertEqual(-10, f.clean('-10'))

    def test_required(self):
        f = RestIntegerField(required=True)
        with self.assertRaises(ValidationError):
            f.clean(None)

        f = RestIntegerField(required=False)
        self.assertEqual(None, f.clean(None))

    def test_initial(self):
        f = RestIntegerField(required=True, initial=123)
        with self.assertRaises(ValidationError):
            f.clean(None)

        f = RestIntegerField(required=False, initial=123)
        self.assertEqual(123, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = RestIntegerField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class IdFieldTest(TestCase):
    def test_string(self):
        f = IdField()
        self.assertEqual(1, f.clean('1'))

    def test_integer(self):
        f = IdField()
        self.assertEqual(2, f.clean(2))

    def test_zero_invalid(self):
        f = IdField()

        with self.assertRaises(ValidationError):
            f.clean("0")

    def test_negative(self):
        f = IdField()

        with self.assertRaises(ValidationError):
            f.clean("-1")

    def test_invalid_format(self):
        f = IdField()

        with self.assertRaises(ValidationError):
            f.clean("1.123")

    def test_with_zero(self):
        f = IdField(with_zero=True)
        self.assertEqual(0, f.clean('0'))

    def test_settings_max_value_not_set(self):
        f = IdField()
        self.assertEqual(2 ** 64 + 1, f.clean(2 ** 64 + 1))

    @override_settings(ID_FIELD_MAX_VALUE=2**64)
    def test_settings_max_value(self):
        f = IdField()
        with self.subTest("Max value"):
            self.assertEqual(2**64, f.clean(2**64))

        with self.subTest("Too big value"):
            with self.assertRaises(ValidationError):
                f.clean(2 ** 64 + 1)

    def test_max_value(self):
        f = IdField(max_value=100)
        with self.subTest("Max value"):
            self.assertEqual(100, f.clean(100))

        with self.subTest("Too big value"):
            with self.assertRaises(ValidationError):
                f.clean(101)

    def test_min_value(self):
        f = IdField(min_value=10)
        with self.subTest("Min value"):
            self.assertEqual(10, f.clean(10))

        with self.subTest("Too small value"):
            with self.assertRaises(ValidationError):
                f.clean(9)

    def test_required(self):
        with self.subTest("required=False"):
            f = IdField(required=False)
            self.assertIsNone(f.clean(None))

        with self.subTest("required=True"):
            f = IdField()

            with self.assertRaises(ValidationError):
                f.clean(None)

    def test_initial(self):
        f = IdArrayField(required=False, initial=1)
        self.assertEqual(1, f.clean(None))


class RestFloatFieldTest(TestCase):
    def test_correct(self):
        f = RestFloatField()
        self.assertEqual(1, f.clean(1))
        f = RestFloatField()
        self.assertEqual(123.456, f.clean(123.456))
        f = RestFloatField()
        self.assertEqual(0, f.clean(0))
        f = RestFloatField()
        self.assertEqual(-10.123, f.clean(-10.123))
        f = RestFloatField()
        self.assertEqual(1, f.clean('1'))
        f = RestFloatField()
        self.assertEqual(123, f.clean('123.0'))
        f = RestFloatField()
        self.assertEqual(0, f.clean('0'))
        f = RestFloatField()
        self.assertEqual(-10, f.clean('-10'))

    def test_required(self):
        f = RestFloatField(required=True)
        with self.assertRaises(ValidationError):
            f.clean(None)

        f = RestFloatField(required=False)
        self.assertEqual(None, f.clean(None))

    def test_initial(self):
        f = RestFloatField(required=True, initial=123.0)
        with self.assertRaises(ValidationError):
            f.clean(None)

        f = RestFloatField(required=False, initial=123.0)
        self.assertEqual(123, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = RestFloatField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class RestCharFieldTest(TestCase):
    def test_required(self):
        f = RestCharField(required=False)
        self.assertEqual(None, f.clean(None))

        f = RestCharField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = "test_string"
        f = RestCharField(required=False, initial=test_data)
        self.assertEqual(test_data, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = RestCharField(required=False, initial='', min_length=1)
        with self.assertRaises(ValidationError):
            f.clean('')

        f2 = RestCharField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f2.clean('')


class RegexFieldValidator(TestCase):
    SRE_MATCH_TYPE = type(re.match("", ""))

    def test_required(self):
        f = RegexField(required=False, regex=r'.*')
        self.assertIsNone(f.clean(None))

        f = RegexField(regex=r'.*')
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = "test_string"
        f = RegexField(required=False, initial=test_data, regex=r'.*')
        self.assertEqual(test_data, f.clean(None))

    def test_regex_valid(self):
        test_data = "test_string"
        f = RegexField(regex=r'^test.*$')
        self.assertEqual(test_data, f.clean(test_data))

    def test_regex_compiled(self):
        test_data = "test_string"
        f = RegexField(regex=re.compile('^test.*$'))
        self.assertEqual(test_data, f.clean(test_data))

    def test_regex_invalid(self):
        test_data = "test_string"
        f = RegexField(regex=r'^test1.*$')
        with self.assertRaises(ValidationError):
            f.clean(test_data)

    def test_init_assertions(self):
        with self.assertRaises(AssertionError):
            RegexField(regex=[])

        with self.assertRaises(AssertionError):
            RegexField(regex=r'', flags=None)

        with self.assertRaises(AssertionError):
            RegexField(regex=r'', flags=[])

    def test_flags(self):
        f = RegexField(regex=r'^test.*$')
        self.assertEqual("test_string", f.clean("test_string"))
        with self.assertRaises(ValidationError):
            f.clean("tESt_string")

        f = RegexField(regex=r'^test.*$', flags=re.I)
        self.assertEqual("test_string", f.clean("test_string"))
        self.assertEqual("tESt_string", f.clean("tESt_string"))

    def test_match(self):
        test_data = "test_string"
        f = RegexField(regex=r'^test(.*)$')
        f.clean(test_data)
        self.assertTrue(isinstance(f.match, self.SRE_MATCH_TYPE))
        self.assertEqual(f.match.group(0), test_data)
        self.assertEqual(f.match.group(1), "_string")

        f = RegexField(regex=r'^test(.*)$', required=False)
        f.clean(None)
        self.assertIsNone(f.match)

    def test_no_regex(self):
        # Acts as a simple CharField
        test_data = "test_string"
        f = RegexField()
        self.assertEqual(test_data, f.clean(test_data))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = RegexField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class RestChoiceFieldTest(TestCase):
    def test_choices_array(self):
        f = RestChoiceField(choices=["a", "b", "c"])
        self.assertEqual("a", f.clean("a"))

    def test_choices_tuples(self):
        f = RestChoiceField(choices=[("a", "a"), ("b", "b"), ("c", "c")])
        self.assertEqual("c", f.clean("c"))

    def test_choices_mixed(self):
        f = RestChoiceField(choices=[("a", "a"), "b", ("c", "c")])
        self.assertEqual("b", f.clean("b"))

    def test_invalid(self):
        f = RestChoiceField(choices=[("a", "a"), "b", ("c", "c")])
        with self.assertRaises(ValidationError):
            f.clean("d")

    def test_empty_string(self):
        f = RestChoiceField(required=False)
        self.assertEqual('', f.clean(''))

        f = RestChoiceField(required=False, choices=['a', 'b', 'c'])
        with self.assertRaises(ValidationError):
            f.clean('')

    def test_required(self):
        f = RestChoiceField(required=False)
        self.assertEqual(None, f.clean(None))

        f = RestChoiceField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = "test_string"
        f = RestChoiceField(required=False, initial=test_data)
        self.assertEqual(test_data, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = RestChoiceField(validators=[TestErrorValidator(0)], choices=['abc', ''])
        with self.assertRaises(ValidationError):
            f.clean('')


class TimestampFieldTest(TestCase):
    def test_now(self):
        now_dt = now().replace(microsecond=0)
        now_ts = to_timestamp(now_dt)
        f = TimestampField()
        res = f.clean(now_ts)
        self.assertEqual(now_dt, res)

    def test_timezones(self):
        dt = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        ts = to_timestamp(dt)
        f = TimestampField()
        res = f.clean(ts)
        self.assertEqual(dt, res)

        dt = datetime.datetime(2017, 1, 1, 0, 0, 0)
        ts = to_timestamp(dt)
        f = TimestampField()
        res = f.clean(ts)
        dt = dt.replace(tzinfo=timezone.utc)
        self.assertEqual(dt, res)

    def test_bounds(self):
        f = TimestampField(in_future=True)
        f.clean(0)
        f.clean(100000000)
        f.clean(2147483647)
        with self.assertRaises(ValidationError):
            f.clean(-random.randint(1, 2147483648))

        with self.assertRaises(ValidationError):
            f.clean(random.randint(2147483648, 4000000000))

    def test_in_future(self):
        f = TimestampField()
        future = now() + datetime.timedelta(hours=1)
        with self.assertRaises(ValidationError):
            f.clean(future)

    def test_initial(self):
        now_dt = now().replace(microsecond=0)
        f = TimestampField(initial=now_dt, required=False)
        res = f.clean(None)
        self.assertEqual(now_dt, res)
        f = TimestampField(initial=to_timestamp(now_dt), required=False)
        res = f.clean(None)
        self.assertEqual(now_dt, res)

    def test_required(self):
        f = TimestampField(required=False)
        self.assertEqual(None, f.clean(None))

        f = TimestampField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = TimestampField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class DateTimeFieldTest(TestCase):
    def test_now(self):
        now_dt = now().replace(microsecond=0)
        f = DateTimeField()
        res = f.clean(now_dt.strftime("%Y-%m-%dT%H:%M:%S"))
        self.assertEqual(now_dt, res)

    def test_initial(self):
        now_dt = now().replace(microsecond=0)
        f = DateTimeField(initial=now_dt, required=False)
        res = f.clean(None)
        self.assertEqual(now_dt, res)

    def test_required(self):
        f = DateTimeField(required=False)
        self.assertEqual(None, f.clean(None))

        f = DateTimeField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = DateTimeField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class DateFieldTest(TestCase):
    def test_today(self):
        today = date.today()
        f = DateField()
        res = f.clean(today.isoformat())
        self.assertEqual(today, res)

    def test_initial(self):
        today = date.today()
        f = DateField(initial=today, required=False)
        res = f.clean(None)
        self.assertEqual(today, res)

    def test_required(self):
        f = DateField(required=False)
        self.assertEqual(None, f.clean(None))

        f = DateField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = DateField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class MonthFieldTest(TestCase):
    def test_now(self):
        now_dt = now().replace(microsecond=0)
        f = MonthField()
        res = f.clean(now_dt.strftime("%Y-%m"))
        self.assertEqual(now_dt.date().replace(day=1), res)

    def test_initial(self):
        f = MonthField(initial='2017-01', required=False)
        res = f.clean(None)
        self.assertEqual(datetime.date(2017, 1, 1), res)

    def test_required(self):
        f = MonthField(required=False)
        self.assertEqual(None, f.clean(None))

        f = MonthField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = MonthField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class DateUnitFieldTest(TestCase):
    def test_day(self):
        f = DateUnitField()
        self.assertEqual('day', f.clean('day'))

    def test_hour(self):
        f = DateUnitField()
        self.assertEqual('hour', f.clean('hour'))

    def test_week(self):
        f = DateUnitField()
        self.assertEqual('week', f.clean('week'))

    def test_invalid(self):
        f = DateUnitField()
        with self.assertRaises(ValidationError):
            f.clean('something')

    def test_required(self):
        f = DateUnitField(required=False)
        self.assertEqual(None, f.clean(None))

        f = DateUnitField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        f = DateUnitField(required=False, initial='day')
        self.assertEqual('day', f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = DateUnitField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('day')


class ColorFieldTest(TestCase):
    def test_color(self):
        f = ColorField()
        self.assertEqual('afafaf', f.clean('afafaf'))

    def test_invalid(self):
        f = ColorField()
        with self.assertRaises(ValidationError):
            f.clean('test')

    def test_required(self):
        f = ColorField(required=False)
        self.assertEqual(None, f.clean(None))

        f = ColorField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        f = ColorField(required=False, initial='afafaf')
        self.assertEqual('afafaf', f.clean(None))


class TruncatedCharFieldTest(TestCase):
    def test_short_string(self):
        f = TruncatedCharField()
        self.assertEqual('afafaf', f.clean('afafaf'))

    def test_no_max(self):
        test_str = 't' * 10000
        f = TruncatedCharField(truncate_length=None)
        self.assertEqual(test_str, f.clean(test_str))

    def test_long_string(self):
        f = TruncatedCharField()
        self.assertEqual(f.clean('t' * 100500), 't' * 255)

    def test_required(self):
        f = TruncatedCharField(required=False)
        self.assertEqual(None, f.clean(None))

        f = TruncatedCharField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        f = TruncatedCharField(required=False, initial='afafaf')
        self.assertEqual('afafaf', f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = TruncatedCharField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class JsonFieldTest(TestCase):
    TEST_SCHEMA = {
        'type': 'object',
        'properties': {
            'test': {
                'type': 'integer',
                'minimum': 1
            }
        }
    }

    def test_json_correct(self):
        test_data = {'test': 1}
        f = JsonField(json_schema=self.TEST_SCHEMA)
        self.assertDictEqual(test_data, f.clean(json.dumps(test_data)))

    def test_json_incorrect(self):
        test_data = {'test': 0}
        f = JsonField(json_schema=self.TEST_SCHEMA)
        with self.assertRaises(ValidationError):
            f.clean(json.dumps(test_data))

    def test_required(self):
        f = JsonField(required=False)
        self.assertEqual(None, f.clean(None))

        f = JsonField()
        self.assertEqual({}, f.clean({}))
        self.assertEqual([], f.clean([]))
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = {'inital': True}
        f = JsonField(required=False, initial=test_data)
        self.assertEqual(test_data, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = JsonField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean({})


class ArrayFieldTest(TestCase):
    def test_json_valid(self):
        f = ArrayField()
        self.assertListEqual([1, 2, 3], f.clean('[1, 2, 3]'))

    def test_json_object(self):
        f = ArrayField()
        with self.assertRaises(ValidationError):
            f.clean('{}')

    def test_json_invalid(self):
        f = ArrayField()
        with self.assertRaises(ValidationError):
            f.clean('[1,2,3')

    def test_comma_separated(self):
        f = ArrayField()
        self.assertListEqual(['1', '2', '3'], f.clean('1,2,3'))

    def test_items_valid(self):
        test_data = [{'test': 1}, {'test': 2}]
        f = ArrayField(item_schema=JsonFieldTest.TEST_SCHEMA)
        self.assertListEqual(test_data, f.clean(json.dumps(test_data)))

    def test_items_invalid(self):
        test_data = [{'test': 1}, {'test': 0}]
        f = ArrayField(item_schema=JsonFieldTest.TEST_SCHEMA)
        with self.assertRaises(ValidationError):
            f.clean(json.dumps(test_data))

    def test_min_items_valid(self):
        test_data = [{'test': 1}]
        f = ArrayField(min_items=1)
        self.assertListEqual(test_data, f.clean(json.dumps(test_data)))

    def test_min_items_invalid(self):
        test_data = []
        f = ArrayField(min_items=1)
        with self.assertRaises(ValidationError):
            f.clean(json.dumps(test_data))

    def test_max_items_valid(self):
        test_data = [{'test': 1}, {'test': 1}]
        f = ArrayField(max_items=2)
        self.assertListEqual(test_data, f.clean(json.dumps(test_data)))

    def test_max_items_invalid(self):
        test_data = [{'test': 1}, {'test': 1}, {'test': 1}]
        f = ArrayField(max_items=2)
        with self.assertRaises(ValidationError):
            f.clean(json.dumps(test_data))

    def test_required(self):
        f = ArrayField(required=False)
        self.assertEqual(None, f.clean(None))

        f = ArrayField()
        self.assertEqual([], f.clean([]))
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = [1, 2, 3]
        f = ArrayField(required=False, initial=test_data)
        self.assertEqual(test_data, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = ArrayField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean([])


class IdArrayFieldTest(TestCase):
    def test_result(self):
        f = IdArrayField()
        self.assertListEqual([1, 2, 3, 4, 3, 1], f.clean('[1, 2, 3, 4, 3, 1]'))
        self.assertListEqual([1, 2, 3, 4, 3, 1], f.clean('["1", "2", "3", "4", "3", "1"]'))

        # Id can't be 0
        with self.assertRaises(ValidationError):
            f.clean('[0, 1, 3, 4]')

    def test_required(self):
        f = IdArrayField(required=False)
        self.assertIsNone(f.clean(None))

        f = IdArrayField()
        self.assertEqual([], f.clean([]))
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = [1, 2, 3]
        f = IdArrayField(required=False, initial=test_data)
        self.assertListEqual(test_data, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = IdArrayField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean([])


class IdSetFieldTest(TestCase):
    def test_result(self):
        f = IdSetField()
        self.assertSetEqual({1, 2, 3, 4}, f.clean('[1, 2, 3, 4, 3, 1]'))
        self.assertSetEqual({1, 2, 3, 4}, f.clean('["1", "2", "3", "4", "3", "1"]'))

        # Id can't be 0
        with self.assertRaises(ValidationError):
            f.clean('[0, 1, 3, 4]')

    def test_required(self):
        f = IdSetField(required=False)
        self.assertIsNone(f.clean(None))

        f = IdSetField()
        self.assertEqual(set(), f.clean([]))
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        test_data = {1, 2, 3}
        f = IdSetField(required=False, initial=test_data)
        self.assertEqual(test_data, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = IdSetField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean([])


class UrlFieldTest(TestCase):
    def test_url_valid(self):
        test_data = 'http://test.ru'
        f = UrlField()
        self.assertEqual(test_data, f.clean(test_data))

    def test_url_invalid(self):
        test_data = 'not_url'
        f = UrlField()
        with self.assertRaises(ValidationError):
            f.clean(test_data)

    def test_required(self):
        f = UrlField(required=False)
        self.assertEqual(None, f.clean(None))

        f = UrlField()
        with self.assertRaises(ValidationError):
            f.clean(None)

    def test_initial(self):
        f = UrlField(required=False, initial='http://test.ru')
        self.assertEqual('http://test.ru', f.clean(None))

    def test_regex(self):
        test_data = 'http://test.ru/test.jpg'
        f = UrlField(regex=r'^.*\.(jpg|jpeg|png|gif)*$', flags=re.I)
        self.assertEqual(test_data, f.clean(test_data))

        f = UrlField(regex=r'^.*\.txt$', flags=re.I)
        with self.assertRaises(ValidationError):
            f.clean(test_data)

    def test_underscore_domain_allowed(self):
        test_data = 'http://test_test.ru/test.jpg'
        f = UrlField()
        self.assertEqual(test_data, f.clean(test_data))

    def test_underscore_domain_rejected(self):
        test_data = 'http://test_test.ru/test.jpg'
        f = UrlField(with_underscore_domain=False)

        with self.assertRaises(ValidationError):
            self.assertEqual(test_data, f.clean(test_data))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = UrlField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class UUIDFieldTest(TestCase):
    def test_uuid_valid(self):
        test_data = str(uuid.uuid4())
        f = UUIDField()
        self.assertEqual(test_data, f.clean(test_data))

    def test_url_invalid(self):
        test_data = 'not_uuid'
        f = UUIDField()
        with self.assertRaises(ValidationError):
            f.clean(test_data)

    def test_required(self):
        f = UUIDField(required=False)
        self.assertEqual(None, f.clean(None))

    def test_initial(self):
        init = str(uuid.uuid4())
        f = UUIDField(required=False, initial=init)
        self.assertEqual(init, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = UUIDField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')


class FileFieldTest(TestCase):
    @staticmethod
    def _get_test_file(extension='txt'):
        f = BytesIO(b'test')
        f.name = 'test.' + extension
        f.size = len(f.getvalue())
        return f

    def test_file_valid(self):
        test_data = self._get_test_file()
        f = FileField()
        self.assertEqual(test_data, f.clean(test_data))

    def test_file_invalid(self):
        f = FileField()
        with self.assertRaises(ValidationError):
            f.clean('123')

    def test_file_extensions(self):
        with self.assertRaises(AssertionError):
            FileField(valid_extensions="test")

        test_file = self._get_test_file('pdf')

        f = FileField(valid_extensions=["pdf", "png"])
        self.assertEqual(test_file, f.clean(test_file))

        test_file.name = 'TEST.PDF'
        self.assertEqual(test_file, f.clean(test_file))

        f = FileField(valid_extensions=["png", "jpg"])
        with self.assertRaises(ValidationError):
            f.clean(f)

    def test_file_size(self):
        with self.assertRaises(AssertionError):
            FileField(max_size="test")

        test_file = self._get_test_file('pdf')

        f = FileField(max_size=2 * 1024 * 1024)
        self.assertEqual(test_file, f.clean(test_file))

        test_file.size = 1 * 1024 * 1024
        self.assertEqual(test_file, f.clean(test_file))

        test_file.size = 2 * 1024 * 1024 - 1
        self.assertEqual(test_file, f.clean(test_file))

        test_file.size = 2 * 1024 * 1024 + 1
        with self.assertRaises(ValidationError):
            f.clean(f)

    def test_required(self):
        f = FileField(required=False)
        self.assertEqual(None, f.clean(None))

    def test_initial(self):
        init = self._get_test_file()
        f = FileField(required=False, initial=init)
        self.assertEqual(init, f.clean(None))

    def test_empty_value_validators(self):
        # By default django skips run_validators methods, if value is in empty_values
        # It's not correct for REST, as empty value is not equal to None value now
        f = FileField(validators=[TestErrorValidator(0)])
        with self.assertRaises(ValidationError):
            f.clean('')
