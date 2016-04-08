# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0020_services_and_methods'),
        ('shoop_testing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentWithCheckoutPhase',
            fields=[
                ('custompaymentprocessor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.CustomPaymentProcessor')),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.custompaymentprocessor',),
        ),
    ]
