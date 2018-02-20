import os

from setuptools import setup

package_name = "brochure_wsgi"
current_directory_path = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(current_directory_path, package_name, 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(name=package_name,
      description="Exposes the brochure application to HTTP clients as a WSGI application",
      version=version,
      include_package_data=True,
      test_suite="tests",
      packages=[
          package_name,
          "{}.deserializers".format(package_name),
          "{}.response_providers".format(package_name),
          "{}.value_fetchers".format(package_name),
      ],
      install_requires=[
          'brochure',
          'Jinja2',
          'Werkzeug',
          'whitenoise'
      ],
      author="Green Light Software, LLC",
      author_email="admin@greenlight.software",
      license="MIT",
      url="https://github.com/GreenLightSoftware/brochure-wsgi")
