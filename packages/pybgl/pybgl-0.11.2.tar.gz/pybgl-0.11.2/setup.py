# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pybgl']

package_data = \
{'': ['*']}

install_requires = \
['ipython>=8.10.0']

setup_kwargs = {
    'name': 'pybgl',
    'version': '0.11.2',
    'description': 'PyBGL is a pure Python graph library inspited from the BGL (Boost Graph Library). It gathers algorithms from the graph theory, language theory and dynamic programming background.',
    'long_description': '# PyBGL\n\n[![PyPI](https://img.shields.io/pypi/v/pybgl.svg)](https://pypi.python.org/pypi/pybgl/)\n[![Build](https://github.com/nokia/pybgl/workflows/build/badge.svg)](https://github.com/nokia/pybgl/actions/workflows/build.yml)\n[![Documentation](https://github.com/nokia/pybgl/workflows/docs/badge.svg)](https://github.com/nokia/pybgl/actions/workflows/docs.yml)\n[![ReadTheDocs](https://readthedocs.org/projects/nokia-pybgl/badge/?version=latest)](https://nokia-pybgl.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/nokia/pybgl/branch/master/graph/badge.svg?token=OZM4J0Y2VL)](https://codecov.io/gh/nokia/pybgl)\n\n## Overview\n\n[PyBGL](https://github.com/nokia/pybgl.git) is a pure [Python](http://python.org/) graph library inspired from the [BGL (Boost Graph Library)](https://www.boost.org/doc/libs/1_80_0/libs/graph/doc/index.html). It gathers algorithms from the graph theory, language theory and dynamic programming background. \n\nFor more information, feel free to visit [the documentation](https://nokia-pybgl.readthedocs.io/en/latest/?badge=latest) and the [wiki](https://github.com/nokia/pybgl/wiki). \n\n# License\n\nThis project is licensed under the BSD-3-Clause license - see the [LICENSE](https://github.com/nokia/pybgl/blob/master/LICENSE).\n',
    'author': 'Marc-Olivier Buob',
    'author_email': 'marc-olivier.buob@nokia-bell-labs.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
