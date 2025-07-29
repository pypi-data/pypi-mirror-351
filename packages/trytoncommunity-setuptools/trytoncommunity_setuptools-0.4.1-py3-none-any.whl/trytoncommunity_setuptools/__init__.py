#!/usr/bin/env python3
# Based on code originally taken from Tryton, heavily
# changed by Tryton Community.
# Copyright (C) the trytoncommunity-setuptools authors
# Copyright (C) 2023-2024 Hartmut Goebel <h.goebel@crazy-compilers.com>
# Copyright (C) 2008-2023 Cédric Krier
# Licensed under the GNU General Public License v3 or later (GPLv3+)
# SPDX-License-Identifier: GPL-3.0-or-later
"""
A wrapper for `setuptools` specialized on Tryton modules

Tryton modules normally contain and require a lot of boilerplate in
`setup.py`.  Not only this is a lot of duplicate code, also it is a burden to
maintain this between different versions of Tryton.

This package allows moving most all the meta-data and options being somewhat
"static" between Tryton modules and Tryton Versions into `setup.cfg` and
using a quite terse `setup.py` only.

`trytoncommunity-setuptools` also supports the 'module prefix mapping` quite
some developers and integrators use.
"""

import re
import textwrap
from configparser import ConfigParser, NoSectionError
from functools import partial
from pathlib import Path

import setuptools

__all__ = ('setup', 'get_require_version', 'get_prefix_require_version',
           'TrytonCommunityURL')

DEFAULT_PACKAGE_DATA_GLOBS = [
    'tryton.cfg', 'view/*.xml', 'locale/*.po', '*.fodt',
    'tests/*.rst', 'tests/*.json', 'icons/*.svg'
]

DEFAULT_CLASSIFIERS = set((
    'Environment :: Plugins',
    'Framework :: Tryton',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Office/Business',
    'Operating System :: OS Independent',
))

SUPPORTED_PYTHON_VERSIONS = {
    # keep aligned with trytoncommunity-cookiecutter-module
    "6.0": ["3.6", "3.7", "3.8", "3.9"],
    "6.2": ["3.6", "3.7", "3.8", "3.9"],
    "6.4": ["3.7", "3.8", "3.9", "3.10"],
    "6.6": ["3.7", "3.8", "3.9", "3.10"],
    "6.8": ["3.8", "3.9", "3.10", "3.11"],
    "7.0": ["3.8", "3.9", "3.10", "3.11", "3.12"],
    "7.2": ["3.8", "3.9", "3.10", "3.11", "3.12"],
    "7.4": ["3.8", "3.9", "3.10", "3.11", "3.12"],
    "7.6": ["3.9", "3.10", "3.11", "3.12", "3.13"],
}


def TrytonCommunityURL(project_path):
    """
    Return a URL string pointing to the 'project_path' within the
    Tryton Community group at heptapod.

       >>> TrytonCommunityURL('modules/country_order')
       https://foss.heptapod.net/tryton-community/modules/country_order
    """
    return ('https://foss.heptapod.net/tryton-community/%s'
            % project_path.strip('/'))


def _read_readme(fname):
    # content = Path(__file__).with_name(fname).read_text('utf-8')
    content = Path(fname).read_text('utf-8')
    content = re.sub(
        r'(?m)^\.\. toctree::\r?\n((^$|^\s.*$)\r?\n)*', '', content)
    return content


def _get_require_version(name, tryton_version, **kw):
    return '%s == %s.*' % (name, tryton_version)


def _get_prefix_require_version(name, tryton_version, module2prefix):
    if '-' in name:
        raise SystemExit("Tryton module names must not contain a dash ('-') "
                         "to keep them aligned with the names in tryton.cfg: "
                         "%r" % name)
    name = '%s-%s' % (module2prefix.get(name, 'trytond'), name)
    return _get_require_version(name, tryton_version=tryton_version)


def get_require_version(name):
    """
    Return a string suitable as a requirement for setuptools with a
    version-specifier matching the Tryton version for the module.

    Example (assuming tryton.cfg says 'version = 6.8.23')::

      get_require_version('proteus') -> 'proteus == 6.8.*'
    """
    return partial(_get_require_version, name)


def get_prefix_require_version(name):
    """
    Like get_require_version(), but the module-name will be prefixed by
    the respective prefix from the `module2prefix` map.

    Example (assuming tryton.cfg says 'version = 6.8.23' and the
    `module2prefix` map contains an entry for 'country_order')::

      get_prefix_require_version('sale') -> 'trytond-sale == 6.8.*'
      get_prefix_require_version('country_order')
         -> 'trytoncommunity-country_order == 6.8.*'
    """
    return partial(_get_prefix_require_version, name)


def _get_supported_python_versions(tryton_version):
    # if the version is not yet defined, use the latest one before
    if tryton_version in SUPPORTED_PYTHON_VERSIONS:
        tv = tryton_version
    else:
        tv = max(v for v in SUPPORTED_PYTHON_VERSIONS if v <= tryton_version)
    return SUPPORTED_PYTHON_VERSIONS[tv]


def _get_classifiers(tryton_version):
    config = ConfigParser()
    config.read('setup.cfg')  # TODO: which encoding is used for this file?
    classifiers = config.get('metadata', 'classifiers', fallback='')
    if not classifiers:
        # try alias
        classifiers = config.get('metadata', 'classifier', fallback='')
    if 'file:' in classifiers:  # TODO
        raise SystemExit(
            "Reading classifiers from 'file:' is not yet supported")
    classifiers = set(c2 for c1 in classifiers.splitlines()
                      for c2 in c1.split(',') if c2)
    classifiers.update(DEFAULT_CLASSIFIERS)
    for pyver in _get_supported_python_versions(tryton_version):
        classifiers.add('Programming Language :: Python :: ' + pyver)
    return list(sorted(classifiers))


def __get_metadata_file_or_section(key):
    config = ConfigParser()
    config.read('setup.cfg')  # TODO: which encoding is used for this file?
    if 'file:' in config.get('metadata', key, fallback=''):
        raise SystemExit(
            "Reading '%s' from 'file:' is not yet supported" % key)
    try:
        value = dict(config.items('options.%s' % key))
    except NoSectionError:
        value = {}
    return value


def setup(prefix, module, module2prefix=None,
          requires=None, tests_require=None, extras_require=None,
          package_data_patterns=None, entry_points="", **kwargs):
    """
    :prefix: prefix of the package, e.g. 'trytoncommunity'
    :name: base name of the module, e.g. 'account_invoice', 'country_order'
    :module2prefix: (dict) mapping module names to package-prefixes,
                    used when auto-generating dependencies from tryton.cfg
    :requires: additional install requires. Dependencies listed in
               tryton.cfg and 'trytond' will be added automatically
    :test_requires: additional packages required for testing
    :extras_require: (dict) passed on to setuptools.setup(), test_requires
                  will be added automatically, if given.
    :package_data_patterns: list of file-globs to be added to the
                  package_data entry passed to setuptools.setup()
    :entry_points: (string) passed on to setuptools.setup(),
                  'trytond.modules' will be added automatically
    """

    def resolve_requirements(requirements):
        return [req(tryton_version=tryton_version, module2prefix=module2prefix)
                if isinstance(req, partial) else req
                for req in (requirements or [])]

    module2prefix = module2prefix or {}
    extras_require = extras_require or {}

    config = ConfigParser()
    # config.read_file(open(Path(__file__).with_name('tryton.cfg')))
    config.read_file(open('tryton.cfg'))
    info = dict(config.items('tryton'))
    for key in ('depends', 'extras_depend', 'xml'):
        if key in info:
            info[key] = info[key].strip().splitlines()
    version = info.get('version', '0.0.1')
    tryton_version = '%s.%s' % tuple(version.split('.', 2)[:2])

    # resolve any delayed evaluation in requires and tests_require
    requires = resolve_requirements(requires)
    tests_require = resolve_requirements(tests_require)

    # collect dependencies from tryton.cfg
    for dep in info.get('depends', []):
        if not re.match(r'(ir|res)(\W|$)', dep):
            requires.append(_get_prefix_require_version(
                dep, tryton_version, module2prefix))
    requires.append(_get_require_version('trytond', tryton_version))

    package_data = (
        info.get('xml', [])
        + (package_data_patterns or [])
        + DEFAULT_PACKAGE_DATA_GLOBS)

    if not extras_require:
        extras_require = __get_metadata_file_or_section('extras_requires')
    if tests_require:
        if 'test' in extras_require:
            raise SystemExit(
                """Must only pass one of 'tests_require' or """
                """'extra_require["tests"]'.""")
        extras_require['test'] = tests_require
        if _get_supported_python_versions(tryton_version) != '6.0.':
            # keep the `tests_require` keyword for 6.0 to still allow
            # running the tests using 'python setup.py test'.
            tests_require = None

    if not entry_points:
        entry_points = __get_metadata_file_or_section('entry_points')
    elif isinstance(entry_points, str):
        config = ConfigParser()
        config.read_string(textwrap.dedent(entry_points))
    else:
        assert isinstance(entry_points, dict)
    if 'trytond.modules' in entry_points:
        raise SystemExit(
            "You must not specify 'trytond.modules' in 'entry_points'. "
            "This will be added automatically.")
    entry_points['trytond.modules'] = (
        '%s = trytond.modules.%s' % (module, module))

    setuptools.setup(
        name='%s_%s' % (prefix, module),
        version=version,
        long_description=_read_readme('README.rst'),
        install_requires=requires,
        tests_require=tests_require,
        extras_require=extras_require,
        python_requires='>= %s' %
            _get_supported_python_versions(tryton_version)[0],  # noqa: E131
        package_dir={'trytond.modules.%s' % module: '.'},
        packages=(
            ['trytond.modules.%s' % module]
            + ['trytond.modules.%s.%s' % (module, p)
               for p in setuptools.find_packages()]
        ),
        package_data={
            'trytond.modules.%s' % module: package_data,
        },
        include_package_data=True,  # of course we want :-)
        zip_safe=False,  # Tryton only supports file-based access yet
        entry_points=entry_points,
        classifiers=_get_classifiers(tryton_version),
        **kwargs,
    )
