# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

import shoop.apps


class DummyAppConfig(shoop.apps.AppConfig):
    name = __name__
    label = 'shoop_tests_dummyapp'


default_app_config = __name__ + '.DummyAppConfig'
