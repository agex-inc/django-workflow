import os
import sys

from setuptools import setup, find_packages

readme_file = os.path.join(os.path.dirname(__file__), 'README.rst')
try:
    long_description = open(readme_file).read()
except IOError as err:
    sys.stderr.write("[ERROR] Cannot find file specified as "
                     "``long_description`` (%s)\n" % readme_file)
    sys.exit(1)

setup(
    name='django-workflow',
    version='3.3.29',
    author='Ahmet DAL',
    author_email='ceahmetdal@gmail.com',
    packages=find_packages(),
    url='https://github.com/javrasya/django-workflow.git',
    description='Django WorkflowModel Library',
    long_description=long_description,
    install_requires=[
        "Django",
        "django-mptt==0.16",
        "django-cte==1.3.3",
        "django-codemirror2==0.2"
    ],
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    platforms=['any'],
)
