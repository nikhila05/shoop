# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import unicode_literals

from django import forms

from shoop.core.models import (
    FixedCostBehaviorComponent, PaymentMethod, ShippingMethod,
    WaivingCostBehaviorComponent, WeightLimitsBehaviorComponent
)
from shoop.utils.multilanguage_model_form import MultiLanguageModelForm


class ShippingMethodForm(MultiLanguageModelForm):
    class Meta:
        model = ShippingMethod
        exclude = [
            "identifier", "behavior_components", "choice_identifier",
            "old_module_identifier", "old_module_data"]

    def __init__(self, **kwargs):
        super(ShippingMethodForm, self).__init__(**kwargs)
        if self.instance.pk and self.instance.carrier:
            choices = [(sc.identifier, sc.name) for sc in self.instance.carrier.get_service_choices()]
            self.fields["choice_identifier"] = forms.ChoiceField(choices=choices)


class PaymentMethodForm(MultiLanguageModelForm):
    class Meta:
        model = PaymentMethod
        exclude = [
            "identifier", "behavior_components", "choice_identifier",
            "old_module_identifier", "old_module_data"]

    def __init__(self, **kwargs):
        super(PaymentMethodForm, self).__init__(**kwargs)
        if self.instance.pk and self.instance.payment_processor:
            choices = [(sc.identifier, sc.name) for sc in self.instance.payment_processor.get_service_choices()]
            self.fields["choice_identifier"] = forms.ChoiceField(choices=choices)


class FixedCostBehaviorComponentForm(MultiLanguageModelForm):
    class Meta:
        model = FixedCostBehaviorComponent
        exclude = ["identifier"]


class WaivingCostBehaviorComponentForm(MultiLanguageModelForm):
    class Meta:
        model = WaivingCostBehaviorComponent
        exclude = ["identifier"]


class WeightLimitsBehaviorComponentForm(forms.ModelForm):
    class Meta:
        model = WeightLimitsBehaviorComponent
        exclude = ["identifier"]
