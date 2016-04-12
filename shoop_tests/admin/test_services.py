# -*- coding: utf-8 -*-
# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

import pytest

from django import forms
from django.conf import settings

from shoop.admin.modules.services.base_form_part import ServiceBaseFormPart
from shoop.admin.modules.services.forms import PaymentMethodForm, ShippingMethodForm
from shoop.admin.modules.services.views import (
    PaymentMethodEditView, ShippingMethodEditView
)
from shoop.apps.provides import override_provides
from shoop.testing.factories import get_default_payment_method, get_default_shipping_method, get_default_shop
from shoop.testing.utils import apply_request_middleware


DEFAULT_BEHAVIOR_FORMS = [
    "shoop.admin.modules.services.forms.FixedCostBehaviorComponentForm",
    "shoop.admin.modules.services.forms.WaivingCostBehaviorComponentForm",
    "shoop.admin.modules.services.forms.WeightLimitsBehaviorComponentForm"
]


def get_form_parts(request, view, object):
    with override_provides("service_behavior_component_form", DEFAULT_BEHAVIOR_FORMS):
        initialized_view = view(request=request, kwargs={"pk": object.pk})
        return initialized_view.get_form_parts(object)


@pytest.mark.django_db
@pytest.mark.parametrize("view,get_object", [
    (PaymentMethodEditView, get_default_payment_method),
    (ShippingMethodEditView, get_default_shipping_method)
])
def test_services_edit_view_formsets(rf, admin_user, view, get_object):
    get_default_shop()
    object = get_object()
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    form_parts = get_form_parts(request, view, object)
    assert len(form_parts) == (len(DEFAULT_BEHAVIOR_FORMS) + 1)  # plus one since the base form


@pytest.mark.django_db
@pytest.mark.parametrize("view", [PaymentMethodEditView, ShippingMethodEditView])
def test_services_edit_view_formsets_in_new_mode(rf, admin_user, view):
    get_default_shop()
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    form_parts = get_form_parts(request, view, view.model())
    assert len(form_parts) == 1
    assert issubclass(form_parts[0].__class__, ServiceBaseFormPart)


@pytest.mark.django_db
@pytest.mark.parametrize("form_class,get_object", [
    (PaymentMethodForm, get_default_payment_method),
    (ShippingMethodForm, get_default_shipping_method)
])
def test_choice_identifier_in_method_form(rf, admin_user, form_class, get_object):
    object = get_object()
    assert object.pk

    # Since object has pk and carrier/payment_processor choice_identifier
    # should be available
    form = form_class(instance=object, languages=settings.LANGUAGES)
    assert "choice_identifier" in form.fields
    assert form.fields["choice_identifier"].widget.__class__ == forms.Select

    if hasattr(object, "carrier"):
        assert getattr(object, "carrier")
        setattr(object, "carrier", None)
    if hasattr(object, "payment_processor"):
        assert getattr(object, "payment_processor")
        setattr(object, "payment_processor", None)

    # No service provider so no choice_identifier-field
    form = form_class(instance=object, languages=settings.LANGUAGES)
    assert "choice_identifier" not in form.fields

    # Let's check cases when the object is not yet saved
    form = form_class(instance=object._meta.model(), languages=settings.LANGUAGES)
    assert "choice_identifier" not in form.fields
