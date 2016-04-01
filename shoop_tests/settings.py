# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

import shoop_workbench.settings
from shoop.utils.setup import Setup


def configure(setup):
    shoop_workbench.settings.configure(setup)
    setup.INSTALLED_APPS += type(setup.INSTALLED_APPS)([
        'shoop_tests.dummyapp',
    ])


globals().update(Setup.configure(configure))
