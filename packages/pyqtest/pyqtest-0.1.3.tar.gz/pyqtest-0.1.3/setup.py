# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from pyqtest import __version__


setup(
    name="pyqtest",
    version=__version__,
    description="Tool for visual testing Qt widgets",
    author="Aleksandr Popov",
    author_email="aleneus@gmail.com",
    license="LGPLv3",
    keywords="testing, TDD, gui",
    url="https://github.com/aleneus/pyqtest",
    py_modules=['pyqtest'],
    install_requires=[
        'PyQt5>=5.15',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
    ],
)
