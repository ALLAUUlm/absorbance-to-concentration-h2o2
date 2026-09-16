# ********************************************************************
#  This file is part of uvv.
#
#        Copyright (C) 2024 Albert Engstfeld
#        Copyright (C) 2024 Alexander Lange
#
#  echemdb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  echemdb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with echemdb. If not, see <https://www.gnu.org/licenses/>.
# ********************************************************************

from distutils.core import setup

setup(
    name='uvv',
    version="0.1.0",
    packages=['uvv'],
    license='GPL 3.0+',
    description="A Python library to work with uvv files.",
    long_description=open('README.md', encoding="UTF-8").read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
      "astropy>=5,<6",
      "unitpackage>=0.8.4,<0.9.0",
      "pandas>=2,<3",
      "ruyaml"
    ],
    python_requires=">=3.9",
)
