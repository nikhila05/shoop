# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2015, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from django import forms
from django.views.generic.edit import FormView

from shoop.front.checkout import CheckoutPhaseViewMixin


class TestCheckoutPhaseTermsForm(forms.Form):
    terms = forms.BooleanField(required=True, label="I promise to pay this order")


class TestCheckoutPhase(CheckoutPhaseViewMixin, FormView):
    module = None
    identifier = "test_payment_phase"
    title = "Test Payment Phase"
    template_name = "shoop_testing/simple_checkout_phase.jinja"
    form_class = TestCheckoutPhaseTermsForm

    def process(self):
        self.request.basket.payment_data["promised_to_pay"] = True
