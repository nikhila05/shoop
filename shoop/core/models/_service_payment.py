# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals, with_statement

from django.db import models
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedFields

from ._order_lines import OrderLineType
from ._orders import PaymentStatus
from ._service_base import Service, ServiceProvider


class PaymentMethod(Service):
    payment_processor = models.ForeignKey(
        "PaymentProcessor", null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("payment processor"))

    translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name=_("name")),
    )

    line_type = OrderLineType.PAYMENT
    provider_attr = 'payment_processor'
    shop_product_m2m = "payment_methods"

    class Meta:
        verbose_name = _("payment method")
        verbose_name_plural = _("payment methods")

    def get_payment_process_response(self, order, urls):
        self._make_sure_is_usable()
        return self.provider.get_payment_process_response(self, order, urls)

    def process_payment_return_request(self, order, request):
        self._make_sure_is_usable()
        self.provider.process_payment_return_request(self, order, request)


class PaymentUrls(object):
    """
    TODO(SHOOP-2293): Document!
    """
    def __init__(self, payment_url, return_url, cancel_url):
        self.payment_url = payment_url
        self.return_url = return_url
        self.cancel_url = cancel_url


class PaymentProcessor(ServiceProvider):
    def get_payment_process_response(self, service, order, urls):
        """
        TODO(SHOOP-2293): Document!

        :type service: shoop.core.models.Service
        :type order: shoop.core.models.Order
        :type urls: PaymentUrls
        :rtype: django.http.HttpResponse|None
        """
        return HttpResponseRedirect(urls.return_url)

    def process_payment_return_request(self, service, order, request):
        """
        TODO(SHOOP-2293): Document!

        Should set ``order.payment_status``.  Default implementation
        just sets it to `~PaymentStatus.DEFERRED` if it is
        `~PaymentStatus.NOT_PAID`.

        :type service: shoop.core.models.Service
        :type order: shoop.core.models.Order
        :type request: django.http.HttpRequest
        :rtype: None
        """
        if order.payment_status == PaymentStatus.NOT_PAID:
            order.payment_status = PaymentStatus.DEFERRED
            order.add_log_entry("Payment status set to deferred by %s" % self)
            order.save(update_fields=("payment_status",))

    def _create_service(self, choice_identifier, **kwargs):
        return PaymentMethod.objects.create(
            payment_processor=self, choice_identifier=choice_identifier, **kwargs)


class CustomPaymentProcessor(PaymentProcessor):
    class Meta:
        verbose_name = _("custom payment processor")
        verbose_name_plural = _("custom payment processors")

    def get_service_choices(self):
        return [self.service_choice('custom', _("Custom payment"))]
