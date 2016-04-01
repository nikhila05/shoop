# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals, with_statement

from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields

from shoop.utils.dates import DurationRange

from ._order_lines import OrderLineType
from ._service_providers import Carrier, PaymentProcessor
from ._services_base import Service


class ShippingMethod(Service):
    carrier = models.ForeignKey(
        Carrier, null=True, blank=True,
        verbose_name=_("carrier"), on_delete=models.SET_NULL)

    translations = TranslatedFields(
        name=models.CharField(_("name"), max_length=100),
    )

    line_type = OrderLineType.SHIPPING
    shop_product_m2m = "shipping_methods"
    provider_attr = 'carrier'

    class Meta:
        verbose_name = _("shipping method")
        verbose_name_plural = _("shipping methods")

    def get_shipping_time(self, source):
        """
        Get shipping time for items in given source.

        :rtype: shoop.utils.dates.DurationRange|None
        """
        times = set()
        for part in self.behavior_parts.all():
            delivery_time = part.get_delivery_time(source)
            if delivery_time:
                assert isinstance(delivery_time, DurationRange)
                times.add(delivery_time.min_duration)
                times.add(delivery_time.max_duration)
        if not times:
            return None
        return DurationRange(min(times), max(times))

    # TODO(SHOOP-2293): Check that method without a provider cannot be saved as enabled


class PaymentMethod(Service):
    payment_processor = models.ForeignKey(
        PaymentProcessor, null=True, blank=True,
        verbose_name=_("payment processor"), on_delete=models.SET_NULL)

    translations = TranslatedFields(
        name=models.CharField(_("name"), max_length=100),
    )

    line_type = OrderLineType.PAYMENT
    provider_attr = 'payment_processor'
    shop_product_m2m = "payment_methods"

    class Meta:
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")

    def get_payment_process_response(self, order, urls):
        self._make_sure_is_usable()
        return self.payment_processor.get_payment_process_response(order, urls)

    def process_payment_return_request(self, order, request):
        self._make_sure_is_usable()
        self.payment_processor.process_payment_return_request(order, request)
