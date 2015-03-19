# coding: utf-8

__author__ = 'Junki Ishida'

from mbserializer._compat import PY26
from setuptools import setup

tests_require=['PyYAML', 'lxml', 'defusedxml', 'pytz', ]
if PY26:
    tests_require.append('ordereddict')

setup(
    name='mbserializer',
    version='0.0.1-alpha',
    description='model based serializer compatible with json, xml and yaml',
    author='Junki Ishida',
    author_email='junkiish@gmail.com',
    url='https://github.com/junkiish/mbserializer',
    packages=['mbserializer', 'mbserializer.fields'],
    license='MIT',
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
