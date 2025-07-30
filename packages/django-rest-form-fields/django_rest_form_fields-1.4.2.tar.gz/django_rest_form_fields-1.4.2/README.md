[![Python unit tests](https://github.com/M1ha-Shvn/django-rest-form-fields/actions/workflows/python-tests.yml/badge.svg)](https://github.com/M1ha-Shvn/django-rest-form-fields/actions/workflows/python-tests.yml)  [![Upload Python Package](https://github.com/M1ha-Shvn/django-rest-form-fields/actions/workflows/python-publish.yml/badge.svg)](https://github.com/M1ha-Shvn/django-rest-form-fields/actions/workflows/python-publish.yml) [![Downloads](https://pepy.tech/badge/django-rest-form-fields/month)](https://pepy.tech/project/django-rest-form-fields)

# django-rest-form-fields
Extended form fields to validate REST-request data via django.forms.

## Requirements
* Python 3.8+  
  Other versions may also work but not tested automatically
* Django 3.2+  
  Other versions may also work but not tested automatically
* typing  
* jsonschema  
  Optional. Required for validating json schema in `JsonField` and its child classes
* pytz  
  Optional. Required for `TimezoneField`

## Installation
Install via pip:  
`pip install django-rest-form-fields`    
or via setup.py:  
`python setup.py install`

## Usage
You can use standard [django forms](https://docs.djangoproject.com/en/1.11/ref/forms/), adding new fields for them.
All `*args` and `**kwargs` fields in reference below will be passed to base django constructors as is.

Example:
```python
from django import forms
from django_rest_form_fields import FileField, ArrayField
    
class MyForm(forms.Form):
    file_field = FileField(max_size=1024, valid_extensions=['valid_extensions'])
    array_field = ArrayField(min_items=1, max_items=10)
            
```

## Base forms
Since version 1.2.2 this library also contains base form classes.
Together with library fields, they give ability to change field's source attribute.
To have this feature, just inherit your class from BaseForm or BaseModelForm:
```python
from django_rest_form_fields.forms import BaseForm
from django_rest_form_fields.fields import RestIntegerField


class MyForm(BaseForm):
    int_field = RestIntegerField(source='intField')
    
f = MyForm({'intField': 123})
f.full_clean()
print(f.cleaned_data['int_field'])
# Outputs: 123
```

## Fields and their options

### RestCharField(*args, source: Optional[str] = None, **kwargs)
Wraps django.forms.forms.CharField:
* Changes default value - None, not empty string
* Fixes initial value (CharField returns empty string, ignoring 'initial' parameter and None value)  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### RegExField(*args, regex: Optional[str] = None, flags: int = 0, source: Optional[str] = None, **kwargs)
RestCharField child class, that automatically validates given string with regex (re.match function)   
If regex parameter is specified and value matches expression, you can get MatchObject using field `match` attribute

Parameters:
* regex: str - regular expression string or compiled with `re.compile()` object
* flags: int - optional validate flags  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### RestChoiceField(*args, choices: Optional[Iterable[Union[str, Tuple[str]]]] = None, source: Optional[str] = None, **kwargs)
Wraps django.forms.forms.ChoiceField:
* Changes default value - None, not empty string
* Fixes initial value (ChoiceField returns empty string, ignoring 'initial' parameter and None value)
* Gives opportunity to set 'choices' as iterable of values, not iterable of tuples  

Parameters:
* choices: Optional[Iterable[Union[str, Tuple[str]]]] - values this field can have. 
    It can be an iterable of strings or iterable of tuples[inner_name: str, human_name: str].
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### RestIntegerField(*args, source: Optional[str] = None, **kwargs)
### RestFloatField(*args, source: Optional[str] = None, **kwargs)
Wrap django.forms.forms.IntegerField and django.forms.forms.FloatField, fixing initial value (Base fields returns None, ignoring 'initial' parameter and None value)  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[int/float]`

### PositiveIntegerField(*args, with_zero: bool = False, source: Optional[str] = None, **kwargs)
Child of RestIntegerField, validating value as positive integer.  

Parameters:
* with_zero: bool - if False, 0 will cause validation error  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[int]`

### IdField(*args, with_zero: bool = False, source: Optional[str] = None, **kwargs)
Child of PositiveIntegerField, validating integer id value.
Upper value can be limited globally with `ID_FIELD_MAX_VALUE` in `django.conf.settings`.  

Resulting value: `Optional[int]`

### TimestampField(*args, in_future: bool = True, source: Optional[str] = None, **kwargs)
Child of RestFloatField. Gets timestamp value and converts it into `datetime.datetime` object in UTC.
Parameter `initial` can be float or `datetime.datetime` value.  
Parameters:
* in_future: bool - if False, datetime is validated to be less than `django.utils.timezone.now()`  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[datetime.datetime]`

### DateTimeField(*args, mask: str = "%Y-%m-%dT%H:%M:%S", source: Optional[str] = None, **kwargs)
Child of RestCharField. Parses datetime string to `datetime.datetime` value.
Parameters:
* mask: str - template for [datetime.strptime](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) function  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[datetime.datetime]`

### MonthField(*args, mask: str = "%Y-%m", source: Optional[str] = None, **kwargs)
Child of DateTimeField. Parses month string to `datetime.date` value.
Returns date of the first day of the month.
Parameters:
* mask: str - template for [datetime.strptime](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) function  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[datetime.date]`

### TimezoneField(*args, source: Optional[str] = None, **kwargs)
Child of RestCharField. Validates string as one of pytz timezone names.

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### DateUnitField(*args, source: Optional[str] = None, **kwargs)
Child of RestChoiceField, validating value as one of [hour, day, week]  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### RestBooleanField(*args, source: Optional[str] = None, **kwargs)
Standard `django.forms.forms.BooleanField` is based on /django/forms/widgets.py `CheckboxInput.value_from_datadict(value)`
It works improperly for REST model: `required=True` + `value=False` => `ValidationError`
This filed fixes this issue, giving opportunity to send False (required or not):
* None as default value
* 'false', '0', '' (ignoring case) as False
* Everything else is parsed with standard bool function  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### LowerCaseEmailField(*args, source: Optional[str] = None, **kwargs)
Wraps `django.forms.forms.EmailField`:
* Converts email string to lowercase
* Fixes initial value bug (EmailField returns empty string, ignoring 'initial' parameter)
* Changes default value - None, not empty string  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### ColorField(*args, source: Optional[str] = None, **kwargs)
Child of RestCharField, validating color.
Color should be six hexadecimal characters.  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### TruncatedCharField(*args, truncate_length: int = 255, source: Optional[str] = None, **kwargs)
Child of RestCharField, which truncates given value, leaving first truncate_length characters.

Parameters:
* truncate_length: Optional[int] - If None, acts as RestCharField. If integer - number of characters to leave.  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### JsonField(*args, json_schema: Optional[dict], source: Optional[str] = None, **kwargs)
Child of RestCharField. Validates, that value is dict, list or JSON-encoded string.
If string - decodes it.  

Parameters:
* json_schema: Optional[dict] - Object to validate given JSON with [jsonschema package](https://pypi.python.org/pypi/jsonschema).
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[Any]`

### ArrayField(*args, min_items: int = 0, max_items: Optional[int] = None, item_schema: Optional[dict] = None, source: Optional[str] = None, **kwargs)
JsonField child. Validates array. It can be represented in 3 forms:
* list instance
* JSON-encoded array
* comma-separated string

Parameters:
* min_items: int - Validates array has more or equal items
* max_items: Optional[int] - Validates array has less or equal items
* item_schema: Optional[dict] - Object to validate every item with [jsonschema package](https://pypi.python.org/pypi/jsonschema).  
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[List[Any]]`

### IdArrayField(*args, source: Optional[str] = None, **kwargs)
ArrayField child. Validates array of IdField().  
Each array element is cleaned with IdField().  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[List[int]]`

### IdSetField(*args, source: Optional[str] = None, **kwargs)
IdArrayField child. Validates set of IdField().  
Each element is cleaned with IdField(). Removes duplicated ids from input, if needed.  

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[Set[int]]`

### UrlField(*args, with_underscore_domain: Optional[bool] = True, source: Optional[str] = None, **kwargs)
RegexField child. Validates string as URL with `django.core.validators.URLValidator`

Parameters:
* with_underscore_domain: Optional[bool] - allow domain with underscore character.
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### HexField(*args, source: Optional[str] = None, **kwargs)
RestCharField child. Validates that string has hexadecimal characters only.

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### UUIDField(*args, source: Optional[str] = None, **kwargs)
RegexField child. Validates field to be correct UUID.

Parameters:
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[str]`

### FileField(*args, max_size: Optional[int] = None, valid_extensions: Optional[List[str]] = None, source: Optional[str] = None, **kwargs)
Wraps django.forms.forms.FileField:
* Fixes initial value bug (FileField returns empty string, ignoring 'initial' parameter)
* Adds validation parameters

Parameters:
* max_size: Optional[int] - File size in bytes
* valid_extensions: Optional[List[str]] - file extensions (without .), that are valid
* source: Optional[str] - name of attribute to get data from. Defaults to form attribute name.

Resulting value: `Optional[file]`


## Running tests
### Running in docker
1. Install [docker and docker-compose](https://www.docker.com/)
2. Run `docker build . --tag django-rest-form-fields` in project directory
3. Run `docker-compose run run_tests` in project directory

### Running in virtual environment
1. Install python
2. [Create virtual environment](https://docs.python.org/3/tutorial/venv.html)
3. Install pip requirements   
  `pip3 install -U -r requirements-test.txt`  
4. Start tests  
  `python3 runtests.py`
