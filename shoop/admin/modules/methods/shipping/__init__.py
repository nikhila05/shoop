# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shoop.admin.base import AdminModule, MenuEntry
from shoop.admin.utils.urls import derive_model_url, get_edit_and_list_urls
from shoop.core.models import ShippingMethod


class ShippingMethodModule(AdminModule):
    name = _("Shipping Methods")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^shipping_method",
            view_template="shoop.admin.modules.methods.shipping.views.ShippingMethod%sView",
            name_template="shipping_method.%s"
        )

    def get_menu_category_icons(self):
        return {self.name: "fa fa-cubes"}

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-truck",
                url="shoop_admin:shipping_method.list",
                category=_("Service Providers")
            )
        ]

    def get_model_url(self, object, kind):
        return derive_model_url(ShippingMethod, "shoop_admin:shipping_method", object, kind)
