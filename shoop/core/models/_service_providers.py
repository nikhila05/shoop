# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from parler.models import TranslatedField

from shoop.core.fields import InternalIdentifierField

from ._base import TranslatableShoopModel
from ._shops import Shop


class ServiceProvider(TranslatableShoopModel):
    identifier = InternalIdentifierField(unique=True)
    enabled = models.BooleanField(default=True, verbose_name=_("enabled"))
    shop = models.ForeignKey(Shop)
    name = TranslatedField()

    class Meta:
        abstract = True

    def get_service_choices(self):
        """
        TODO(SHOOP-2293): Document!

        You may use `service_choice` to create the service choices.

        :rtype: list[ServiceChoice]
        """
        raise NotImplementedError

    @classmethod
    def service_choice(cls, identifier, name):
        """
        TODO(SHOOP-2293): Document!

        :rtype: ServiceChoice
        """
        return ServiceChoice(identifier, name)

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
