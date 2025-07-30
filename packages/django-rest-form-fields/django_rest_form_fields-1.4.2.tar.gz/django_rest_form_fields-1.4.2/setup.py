from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = []
with open('requirements.txt') as f:
    for line in f.readlines():
        line = line.strip()  # Remove spaces
        line = line.split('#')[0]  # Remove comments
        if line:  # Remove empty lines
            requires.append(line)

setup(
    name='django-rest-form-fields',
    version='1.4.2',
    packages=['django_rest_form_fields'],
    package_dir={'': 'src'},
    url='https://github.com/M1hacka/django-rest-form-fields',
    license='BSD 3-clause "New" or "Revised" License',
    author='Mikhail Shvein',
    author_email='work_shvein_mihail@mail.ru',
    description='Extended form fields to validate REST-request data via django.forms',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requires
)
