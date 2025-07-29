from setuptools import setup
import re
project_name = 'PyJotformAJM'


def get_property(prop, project):
    result = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), open(project + '/_version.py').read())
    return result.group(1)


setup(
    name=project_name,
    version=get_property('__version__', project_name),
    packages=['PyJotformAJM'],
    install_requires=['jotform', 'ApiKeyAJM'],
    url='https://github.com/amcsparron2793-Water/PyJotformAJM',
    download_url=f'https://github.com/amcsparron2793-Water/PyJotformAJM/archive/refs/tags/{get_property("__version__", project_name)}.tar.gz',
    keywords=[],
    license='MIT License',
    author='Amcsparron',
    author_email='amcsparron@albanyny.gov',
    description='*** Overall project description goes here ***'
)
