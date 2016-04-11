# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import unicode_literals

import functools
import random
from collections import defaultdict

import six
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.managers import TranslatableQuerySet
from parler.models import TranslatedField, TranslatedFields

from shoop.core.fields import InternalIdentifierField
from shoop.core.pricing import PriceInfo

from ._base import (
    PolymorphicShoopModel, PolymorphicTranslatableShoopModel,
    PolyTransModelBase, TranslatableShoopModel
)
from ._product_shops import ShopProduct
from ._shops import Shop


class ServiceChoice(object):
    def __init__(self, identifier, name):
        """
        Initialize service choice.

        :type identifier: str
        :param identifier:
          Internal identifier for the service.  Should be unique within
          a single `ServiceProvider`.
        :type name: str
        :param name:
          Descriptive name of the service in currently active language.
        """
        self.identifier = identifier
        self.name = name


class ServiceProvider(PolymorphicTranslatableShoopModel):
    identifier = InternalIdentifierField(unique=True, verbose_name=_("identifier"))
    enabled = models.BooleanField(default=True, verbose_name=_("enabled"))
    name = TranslatedField(any_language=True)

    base_translations = TranslatedFields(
        name=models.CharField(max_length=100, verbose_name=_("name")),
    )

    checkout_phase_class = None

    #: Helper for creating `ServiceChoice` objects.
    service_choice = ServiceChoice

    def get_service_choices(self):
        """
        Retrieve all ``ServiceChoice`` objects for this provider.
        Subclass should implement this method.

        You may use `service_choice` to create the service choices.

        :rtype: list[ServiceChoice]
        """
        raise NotImplementedError

    def create_service(self, choice_identifier, **kwargs):
        """
        Create ``Service`` object based on choice_identifier parameter.
        Actual _create_service-method should be implemented in subclass.

        May attach some behavior components (`ServiceBehaviorComponent`)
        to the created service.

        :type choice_identifier: str|None
        :param choice_identifier:
          Identifier of the service choice to use.  If None, use the
          default service choice.
        :rtype: shoop.core.models.Service
        """
        if choice_identifier is None:
            choice_identifier = self.get_service_choices()[0].identifier
        return self._create_service(choice_identifier, **kwargs)

    def _create_service(self, choice_identifier, **kwargs):
        raise NotImplementedError

    def get_effective_name(self, service, source):
        """
        Get effective name of the service for given order source.

        Base class implementation will just return name of the given
        service, but that may be changed in a subclass.

        :type service: shoop.core.models.Service
        :type source: shoop.core.order_creator.OrderSource
        :rtype: str
        """
        return service.name

    def get_checkout_phase(self, service, **kwargs):
        """
        :type service: shoop.core.models.Service
        :rtype: shoop.front.checkout.CheckoutPhaseViewMixin|None
        """
        phase_class = self.checkout_phase_class
        if not phase_class:
            return None
        from shoop.front.checkout import CheckoutPhaseViewMixin
        assert issubclass(phase_class, CheckoutPhaseViewMixin)
        return phase_class(service=service, **kwargs)


class ServiceQuerySet(TranslatableQuerySet):
    def enabled(self):
        no_provider_filter = {
            self.model.provider_attr: None,
        }
        enabled_filter = {
            self.model.provider_attr + '__enabled': True,
            'enabled': True,
        }
        return self.exclude(**no_provider_filter).filter(**enabled_filter)

    def for_shop(self, shop):
        return self.filter(shop=shop)

    def available_ids(self, shop, products):
        """
        Retrieve common available services for a shop and product IDs.

        :param shop_id: Shop ID
        :type shop_id: int
        :param product_ids: Product IDs
        :type product_ids: set[int]
        :return: Set of service IDs
        :rtype: set[int]
        """
        shop_product_m2m = self.model.shop_product_m2m
        shop_product_limiter_attr = "limit_%s" % self.model.shop_product_m2m

        limiting_products_query = {
            "shop": shop,
            "product__in": products,
            shop_product_limiter_attr: True
        }
        enabled_for_shop = self.enabled().for_shop(shop)
        available_ids = set(enabled_for_shop.values_list("pk", flat=True))

        for shop_product in ShopProduct.objects.filter(**limiting_products_query):
            available_ids &= set(getattr(shop_product, shop_product_m2m).values_list("pk", flat=True))
            if not available_ids:  # Out of IDs, better just fail fast
                break

        return available_ids

    def available(self, shop, products):
        return self.filter(pk__in=self.available_ids(shop, products))


class Service(TranslatableShoopModel):
    identifier = InternalIdentifierField(unique=True, verbose_name=_("identifier"))
    enabled = models.BooleanField(default=True, verbose_name=_("enabled"))
    shop = models.ForeignKey(Shop, blank=True, null=True, verbose_name=_("shop"))

    # Initialized from ServiceChoice.identifier
    choice_identifier = models.CharField(blank=True, max_length=64, verbose_name=_("choice identifier"))

    name = TranslatedField(any_language=True)

    tax_class = models.ForeignKey(
        'TaxClass', on_delete=models.PROTECT, verbose_name=_("tax class"))

    objects = ServiceQuerySet.as_manager()

    behavior_components = models.ManyToManyField('ServiceBehaviorComponent', verbose_name=_("behavior components"))

    class Meta:
        abstract = True

    @property
    def provider(self):
        """
        :rtype: shoop.core.models.ServiceProvider
        """
        return getattr(self, self.provider_attr)

    def get_checkout_phase(self, **kwargs):
        """
        :rtype: shoop.core.front.checkout.CheckoutPhaseViewMixin|None
        """
        return self.provider.get_checkout_phase(service=self, **kwargs)

    def get_effective_name(self, source):
        """
        Get effective name of the service for given order source.

        By default, effective name is the same as name of this service,
        but if there is a service provider with a custom implementation
        for `~shoop.core.models.ServiceProvider.get_effective_name`
        method, then this can be different.

        :type source: shoop.core.order_creator.OrderSource
        :rtype: str
        """
        if not self.provider:
            return self.name
        return self.provider.get_effective_name(self, source)

    def is_available_for(self, source):
        """
        Return true if service is available for given source.

        :type source: shoop.core.order_creator.OrderSource
        :rtype: bool
        """
        return not any(self.get_unavailability_reasons(source))

    def get_unavailability_reasons(self, source):
        """
        Get reasons of being unavailable for given source.

        :type source: shoop.core.order_creator.OrderSource
        :rtype: Iterable[ValidationError]
        """
        if not self.provider or not self.provider.enabled or not self.enabled:
            yield ValidationError(_("%s is disabled") % self, code='disabled')

        if source.shop != self.shop:
            yield ValidationError(
                _("%s is for different shop") % self, code='wrong_shop')

        for component in self.behavior_components.all():
            for reason in component.get_unavailability_reasons(self, source):
                yield reason

    def get_total_cost(self, source):
        """
        Get total cost of this service for items in given source.

        :type source: shoop.core.order_creator.OrderSource
        :rtype: PriceInfo
        """
        price_infos = (x.price_info for x in self.get_costs(source))
        zero = source.create_price(0)
        return _sum_price_infos(price_infos, PriceInfo(zero, zero, quantity=1))

    def get_costs(self, source):
        """
        Get costs of this service for items in given source.

        :type source: shoop.core.order_creator.OrderSource
        :return: description, price and tax class of the costs
        :rtype: Iterable[Cost]
        """
        for component in self.behavior_components.all():
            for cost in component.get_costs(self, source):
                yield Cost(
                    price=cost.price,
                    description=cost.description,
                    tax_class=(cost.tax_class or self.tax_class),
                    base_price=cost.base_price)

    def get_lines(self, source):
        """
        Get lines for given source.

        :type source: shoop.core.order_creator.OrderSource
        :rtype: Iterable[shoop.core.order_creator.SourceLine]
        """
        line_prefix = type(self).__name__.lower()
        costs = (
            list(self.get_costs(source)) or
            [Cost(source.create_price(0), None, self.tax_class)])
        costs_without_description = defaultdict(list)
        line_no = 0
        for cost in costs:
            if cost.description:
                line_no += 1
                description = _('%(service_name)s: %(sub_item)s') % {
                    'service_name': self, 'sub_item': cost.description}
            else:
                costs_without_description[cost.tax_class].append(cost)
                continue
            yield self._get_line(source, line_prefix, line_no, cost.price_info, cost.tax_class, description)

        for tax_class, costs_for_tax_class in six.iteritems(costs_without_description):
            line_no += 1
            zero = source.create_price(0)
            price_info = _sum_price_infos(
                [cost.price_info for cost in costs_for_tax_class],
                PriceInfo(zero, zero, quantity=1))
            yield self._get_line(source, line_prefix, line_no, price_info, tax_class)

    def _get_line(self, source, line_prefix, line_no, price_info, tax_class, description=None):
        def rand_int():
            return random.randint(0, 0x7FFFFFFF)

        return source.create_line(
            line_id="%s_%02d_%x" % (line_prefix, line_no, rand_int()),
            type=self.line_type,
            quantity=price_info.quantity,
            text=(description or self.get_effective_name(source)),
            base_unit_price=price_info.base_unit_price,
            discount_amount=price_info.discount_amount,
            tax_class=tax_class,
        )

    def _make_sure_is_usable(self):
        if not self.provider:
            raise ValueError('%r has no %s' % (self, self.provider_attr))
        if not self.enabled:
            raise ValueError('%r is disabled' % (self,))
        if not self.provider.enabled:
            raise ValueError(
                '%s of %r is disabled' % (self.provider_attr, self))


def _sum_price_infos(price_infos, zero):
    def plus(pi1, pi2):
        assert pi1.quantity == pi2.quantity
        return PriceInfo(
            pi1.price + pi2.price,
            pi1.base_price + pi2.base_price,
            quantity=pi1.quantity,
        )
    return functools.reduce(plus, price_infos, zero)


class Cost(object):
    def __init__(
            self, price, description=None,
            tax_class=None, base_price=None):
        """
        :type price: shoop.core.pricing.Price
        :type description: str|None
        :type tax_class: shoop.core.models.TaxClass|None
        :type base_price: shoop.core.pricing.Price|None
        """
        self.price = price
        self.description = description
        self.tax_class = tax_class
        self.base_price = base_price if base_price is not None else price

    @property
    def price_info(self):
        return PriceInfo(self.price, self.base_price, quantity=1)


class ServiceBehaviorComponent(PolymorphicShoopModel):
    #: Name for the component (lazy translated)
    name = None

    #: Help text for the component (lazy translated)
    help_text = None

    #: Helper for creating `Cost` objects.
    cost = Cost

    def __init__(self, *args, **kwargs):
        if type(self) != ServiceBehaviorComponent and self.name is None:
            raise TypeError('%s.name is not defined' % type(self).__name__)
        super(ServiceBehaviorComponent, self).__init__(*args, **kwargs)

    def get_unavailability_reasons(self, service, source):
        """
        :type service: Service
        :type source: shoop.core.order_creator.OrderSource
        :rtype: Iterable[ValidationError]
        """
        return ()

    def get_costs(self, service, source):
        """
        Return costs for for this object. This should be implemented
        in subclass. This method is used to calculate price for
        ``ShippingMethod`` and ``PaymentMethod`` objects.

        Costs may be created with the `cost` helper.

        :type service: Service
        :type source: shoop.core.order_creator.OrderSource
        :rtype: Iterable[Cost]
        """
        return ()

    def get_delivery_time(self, service, source):
        """
        :type service: Service
        :type source: shoop.core.order_creator.OrderSource
        :rtype: shoop.utils.dates.DurationRange|None
        """
        return None


class TranslatableServiceBehaviorComponent(six.with_metaclass(
        PolyTransModelBase,
        ServiceBehaviorComponent, TranslatableShoopModel)):
    class Meta:
        abstract = True
