# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import unicode_literals

from shoop.admin.forms.widgets import MediaChoiceWidget
from shoop.core.models import CustomCarrier, CustomPaymentProcessor
from shoop.utils.multilanguage_model_form import MultiLanguageModelForm


class CustomCarrierForm(MultiLanguageModelForm):
    class Meta:
        model = CustomCarrier
        exclude = ("identifier", )

    def __init__(self, **kwargs):
        super(CustomCarrierForm, self).__init__(**kwargs)
        self.fields["logo"].widget = MediaChoiceWidget(clearable=True)


class CustomPaymentProcessorForm(MultiLanguageModelForm):
    class Meta:
        model = CustomPaymentProcessor
        exclude = ("identifier", )

    def __init__(self, **kwargs):
        super(CustomPaymentProcessorForm, self).__init__(**kwargs)
        self.fields["logo"].widget = MediaChoiceWidget(clearable=True)
