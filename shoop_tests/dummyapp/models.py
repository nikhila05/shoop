# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from shoop.core.fields import MoneyValueField
from shoop.core.models import ServiceBehaviorPart
from shoop.core.pricing import PriceInfo


class ExpensiveSwedenBehaviorPart(ServiceBehaviorPart):
    def get_name(self, service, source):
        return "Expenseefe-a Svedee Sheepping"

    def get_costs(self, service, source):
        four = source.create_price('4.00')
        five = source.create_price('5.00')
        if source.shipping_address and source.shipping_address.country == "SE":
            yield (None, PriceInfo(five, four, 1), None)
        else:
            yield (None, PriceInfo(four, four, 1), None)

    def get_unavailability_reasons(self, service, source):
        if source.shipping_address and source.shipping_address.country == "FI":
            yield ValidationError("Veell nut sheep unytheeng tu Feenlund!", code="we_no_speak_finnish")


class PriceWaiverBehaviorPart(ServiceBehaviorPart):
    waive_limit_value = MoneyValueField()

    def get_costs(self, service, source):
        waive_limit = source.create_price(self.waive_limit_value)
        product_total = source.total_price_of_products
        if product_total and product_total >= waive_limit:
            five = source.create_price(5)
            # TODO(SHOOP-2293): Reconsider calculation of method's price
            # with behavior parts since price waiving is impossible
            #
            # We decided to use campaigns in that case... maybe that's
            # OK too, but then these test would have to be amended and
            # the Campaign rule has to be created
            yield (_("Free shipping"), PriceInfo(-five, -five, 1), None)
