# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedField, TranslatedFields

from shoop.core.fields import InternalIdentifierField

from ._base import PolymorphicTranslatableShoopModel
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
    identifier = InternalIdentifierField(unique=True)
    enabled = models.BooleanField(default=True, verbose_name=_("enabled"))
    shop = models.ForeignKey(Shop)
    name = TranslatedField(any_language=True)

    base_translations = TranslatedFields(
        name=models.CharField(_("name"), max_length=100),
    )

    checkout_phase_class = None

    #: Helper for creating `ServiceChoice` objects.
    service_choice = ServiceChoice

    def get_service_choices(self):
        """
        TODO(SHOOP-2293): Document!

        You may use `service_choice` to create the service choices.

        :rtype: list[ServiceChoice]
        """
        raise NotImplementedError

    def create_service(self, choice_identifier, **kwargs):
        """
        TODO(SHOOP-2293): Document!

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
