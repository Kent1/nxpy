#!/usr/bin/env python
# Copyright 2011 Leonidas Poulopoulos (GRNET S.A - NOC)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.core import setup

setup(name='nxpy',
      version='0.4.1',
      description='Network Device XML configuration to Python Proxy',
      author='Leonidas Poulopoulos (GRNET NOC)',
      author_email='leopoul@noc.grnet.gr',
      packages=['nxpy'],
      license="Apache License 2.0",
      platforms=["Posix; OS X; Windows"],
     )

