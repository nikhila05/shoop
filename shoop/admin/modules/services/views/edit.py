# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import six
from django.conf import settings
from django.db.transaction import atomic

from shoop.admin.form_part import (
    FormPart, FormPartsViewMixin, SaveFormPartsMixin, TemplatedFormDef
)
from shoop.admin.modules.services.forms import (
    PaymentMethodForm, ShippingMethodForm
)
from shoop.admin.utils.views import CreateOrUpdateView
from shoop.apps.provides import get_provide_specs_and_objects
from shoop.core.models import PaymentMethod, ShippingMethod
from shoop.utils.form_group import FormDef
from shoop.utils.multilanguage_model_form import TranslatableModelForm


class ServiceBaseFormPart(FormPart):
    priority = -1000  # Show this first
    form = None  # Override in subclass

    def __init__(self, *args, **kwargs):
        super(ServiceBaseFormPart, self).__init__(*args, **kwargs)

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            self.form,
            required=True,
            template_name="shoop/admin/services/_edit_base_form.jinja",
            kwargs={"instance": self.object, "languages": settings.LANGUAGES}
        )

    def form_valid(self, form):
        self.object = form["base"].save()
        return self.object


class ShippingMethodBaseFormPart(ServiceBaseFormPart):
    form = ShippingMethodForm


class PaymentMethodBaseFormPart(ServiceBaseFormPart):
    form = PaymentMethodForm


class BehaviorComponentFormPart(FormPart):
    def __init__(self, request, form, name, owner):
        self.name = name
        self.form = form
        self.owner = owner
        model_class = form._meta.model
        components = owner.behavior_components
        self.object = components.instance_of(model_class).first()  # TODO (SHOOP-2336): self.object should be owner
        super(BehaviorComponentFormPart, self).__init__(request, object=self.object)

    def get_form_defs(self):
        kwargs = {}
        if issubclass(self.form, TranslatableModelForm):
            kwargs["languages"] = settings.LANGUAGES
        if self.object:
            kwargs["instance"] = self.object
        yield FormDef(
            self.name,
            self.form,  # TODO (SHOOP-2336): Make this formset
            required=False,
            kwargs=kwargs,
        )

    def form_valid(self, form):
        component_form = form[self.name]
        # TODO (SHOOP-2336): This should probably live under formset
        if component_form.is_valid() and component_form.cleaned_data:
            component = component_form.save()
            if component not in self.owner.behavior_components.all():
                self.owner.behavior_components.add(component)


class ServiceEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = None
    template_name = "shoop/admin/services/edit.jinja"
    context_object_name = "shipping_method"
    base_form_part_classes = []  # Override in subclass
    provide_key = "service_behavior_component_form"

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_form_parts(self, object):
        form_parts = super(ServiceEditView, self).get_form_parts(object)
        provides_forms = get_provide_specs_and_objects(self.provide_key)
        for spec, form in six.iteritems(provides_forms):
            form_parts.append(self._get_behavior_form_part(spec, form, object))
        return form_parts

    def _get_behavior_form_part(self, spec, form, object):
        name = spec.replace(":", "").replace(".", "")  # Take out delimiters characters
        if not object.pk or not hasattr(form._meta, "model"):
            return None
        return BehaviorComponentFormPart(self.request, form, name, object)


class ShippingMethodEditView(ServiceEditView):
    model = ShippingMethod
    base_form_part_classes = [ShippingMethodBaseFormPart]


class PaymentMethodEditView(ServiceEditView):
    model = PaymentMethod
    base_form_part_classes = [PaymentMethodBaseFormPart]
