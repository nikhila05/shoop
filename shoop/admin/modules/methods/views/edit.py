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

from shoop.admin.modules.methods.shipping.forms import ShippingMethodForm
from shoop.admin.form_part import (
    FormPart, FormPartsViewMixin, SaveFormPartsMixin, TemplatedFormDef
)
from shoop.admin.utils.views import CreateOrUpdateView
from shoop.apps.provides import get_provide_specs_and_objects
from shoop.core.models import ShippingMethod
from shoop.utils.form_group import FormDef
from shoop.utils.multilanguage_model_form import TranslatableModelForm


def _get_default_component(components, form_class, form=None):
    if not hasattr(form_class._meta, "model"):
        return None
    model_class = form_class._meta.model
    component = components.instance_of(model_class).first()
    if not component and form:
        component = form.save()
        components.add(component)
    return component


class MethodBaseFormPart(FormPart):
    priority = -1000  # Show this first

    def __init__(self, *args, **kwargs):
        super(MethodBaseFormPart, self).__init__(*args, **kwargs)
        # Make this more general
        # self.method_form = kwargs["method_form_class"]

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            ShippingMethodForm,
            required=True,
            template_name="shoop/admin/shipping_methods/_edit_base_form.jinja",
            kwargs={
                "instance": self.object,
                "languages": settings.LANGUAGES,
            }
        )

    def form_valid(self, form):
        self.object = form["base"].save()
        return self.object


class MethodEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = ShippingMethod
    template_name = "shoop/admin/shipping_methods/edit.jinja"
    context_object_name = "shipping_method"
    base_form_part_classes = [
        MethodBaseFormPart,
    ]
    behavior_component_form_names = []

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_form_parts(self, object):
        form_parts = super(MethodEditView, self).get_form_parts(object)
        provides_forms = get_provide_specs_and_objects("shipping_method_behavior_component_forms")
        for spec, form in six.iteritems(provides_forms):
            name = spec.replace(":", "").replace(".", "")  # Take out delimiters characters
            if name not in self.behavior_component_form_names:
                self.behavior_component_form_names.append(name)
            default = _get_default_component(object.behavior_components, form)
            form_parts.append(BehaviorComponentFormPart(name, form, self.request, object=default))
        return form_parts

    def get_context_data(self, **kwargs):
        data = super(MethodEditView, self).get_context_data(**kwargs)
        data["behavior_component_form_names"] = self.behavior_component_form_names
        return data


class BehaviorComponentFormPart(FormPart):
    def __init__(self, form_name, form_class, request, object=None):
        super(BehaviorComponentFormPart, self).__init__(request, object=object)
        self.form_name = form_name
        self.form_class = form_class

    def get_form_defs(self):
        kwargs = {}
        if issubclass(self.form_class, TranslatableModelForm):
            kwargs["languages"] = settings.LANGUAGES
        if self.object:
            kwargs["instance"] = self.object
        yield FormDef(
            self.form_name,
            self.form_class,
            required=False,
            kwargs=kwargs,
        )

    def form_valid(self, form):
        component_form = form[self.form_name]
        if component_form.is_valid():
            component_form.save()
