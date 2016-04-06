# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import unicode_literals

from django import forms
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from shoop.admin.base import MenuEntry
from shoop.admin.utils.views import CreateOrUpdateView
from shoop.apps.provides import get_provide_objects
from shoop.core.models import ServiceProvider
from shoop.utils.iterables import first


def _get_model(form):
    return form._meta.model


def _get_type_choice_value(form):
    return _get_model(form).__name__


def _get_type_choices(forms):
    choices = []
    for form in forms:
        choices.append((_get_type_choice_value(form), _get_model(form)._meta.verbose_name.capitalize()))
    return choices


class _BaseMethodEditView(CreateOrUpdateView):
    model = ServiceProvider  # Overridden below
    action_url_name_prefix = None
    template_name = "shoop/admin/service_providers/edit.jinja"
    form_class = forms.Form
    context_object_name = "service_provider"
    default_provider_models = []
    provider_model_provide_key = ""
    add_form_errors_as_messages = True

    @property
    def title(self):
        return _(u"Edit %(model)s") % {"model": self.model._meta.verbose_name}

    def get_breadcrumb_parents(self):
        return [
            MenuEntry(
                text=force_text(self.model._meta.verbose_name_plural).title(),
                url="shoop_admin:%s.list" % self.action_url_name_prefix
            )
        ]

    def get_form(self, form_class=None):
        provider_service_forms = list(get_provide_objects(self.provider_model_provide_key))
        if self.object and self.object.pk:
            self.form_class = first(
                f for f in provider_service_forms if isinstance(self.object, _get_model(f))
            )
            return self.form_class(**self.get_form_kwargs())
        else:
            selected_type = self.request.GET.get("type")
            self.form_class = provider_service_forms[0]
            if selected_type:
                self.form_class = first(
                    f for f in provider_service_forms if selected_type == _get_type_choice_value(f)
                )

            self.object = _get_model(self.form_class)()
            form = self.form_class(**self.get_form_kwargs())
            form.fields["type"] = forms.ChoiceField(
                choices=_get_type_choices(provider_service_forms),
                label=_("Type"),
                required=False,
                initial=_get_type_choice_value(self.form_class)
            )
            return form

    def get_success_url(self):
        return reverse("shoop_admin:%s.edit" % self.action_url_name_prefix, kwargs={"pk": self.object.pk})

    def save_form(self, form):
        self.object = form.save()


class CarrierEditView(_BaseMethodEditView):
    action_url_name_prefix = "service_provider.carrier"
    provider_model_provide_key = "carrier_model"


class PaymentProcessorEditView(_BaseMethodEditView):
    action_url_name_prefix = "service_provider.payment_processor"
    provider_model_provide_key = "payment_processor_model"
