# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shoop.core.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('shoop', '0019_contact_merchant_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceBehaviorComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('identifier', shoop.core.fields.InternalIdentifierField(null=True, unique=True, max_length=64, blank=True, editable=False)),
                ('enabled', models.BooleanField(verbose_name='enabled', default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProviderTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('language_code', models.CharField(verbose_name='Language', max_length=15, db_index=True)),
                ('name', models.CharField(verbose_name='name', max_length=100)),
            ],
            options={
                'managed': True,
                'db_table': 'shoop_serviceprovider_translation',
                'default_permissions': (),
                'verbose_name': 'service provider Translation',
                'db_tablespace': '',
            },
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='module_data',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='module_identifier',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='status',
        ),
        migrations.RemoveField(
            model_name='shippingmethod',
            name='module_data',
        ),
        migrations.RemoveField(
            model_name='shippingmethod',
            name='module_identifier',
        ),
        migrations.RemoveField(
            model_name='shippingmethod',
            name='status',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='choice_identifier',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='enabled',
            field=models.BooleanField(verbose_name='enabled', default=True),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='choice_identifier',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='enabled',
            field=models.BooleanField(verbose_name='enabled', default=True),
        ),
        migrations.AlterField(
            model_name='paymentmethodtranslation',
            name='name',
            field=models.CharField(verbose_name='name', max_length=100),
        ),
        migrations.AlterField(
            model_name='shippingmethodtranslation',
            name='name',
            field=models.CharField(verbose_name='name', max_length=100),
        ),
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('serviceprovider_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.ServiceProvider', parent_link=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.serviceprovider',),
        ),
        migrations.CreateModel(
            name='FixedCostBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.ServiceBehaviorComponent', parent_link=True, serialize=False)),
                ('price_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent',),
        ),
        migrations.CreateModel(
            name='PaymentProcessor',
            fields=[
                ('serviceprovider_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.ServiceProvider', parent_link=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.serviceprovider',),
        ),
        migrations.CreateModel(
            name='WaivingCostBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.ServiceBehaviorComponent', parent_link=True, serialize=False)),
                ('price_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
                ('waive_limit_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent',),
        ),
        migrations.CreateModel(
            name='WeightLimitsBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.ServiceBehaviorComponent', parent_link=True, serialize=False)),
                ('min_weight', models.DecimalField(null=True, verbose_name='minimum weight', blank=True, decimal_places=6, max_digits=36)),
                ('max_weight', models.DecimalField(null=True, verbose_name='maximum weight', blank=True, decimal_places=6, max_digits=36)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent',),
        ),
        migrations.AddField(
            model_name='serviceprovidertranslation',
            name='master',
            field=models.ForeignKey(null=True, related_name='translations', to='shoop.ServiceProvider', editable=False),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='polymorphic_ctype',
            field=models.ForeignKey(null=True, related_name='polymorphic_shoop.serviceprovider_set+', to='contenttypes.ContentType', editable=False),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='shop',
            field=models.ForeignKey(to='shoop.Shop'),
        ),
        migrations.AddField(
            model_name='servicebehaviorcomponent',
            name='polymorphic_ctype',
            field=models.ForeignKey(null=True, related_name='polymorphic_shoop.servicebehaviorcomponent_set+', to='contenttypes.ContentType', editable=False),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='behavior_components',
            field=models.ManyToManyField(to='shoop.ServiceBehaviorComponent'),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='behavior_components',
            field=models.ManyToManyField(to='shoop.ServiceBehaviorComponent'),
        ),
        migrations.CreateModel(
            name='CustomCarrier',
            fields=[
                ('carrier_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.Carrier', parent_link=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.carrier',),
        ),
        migrations.CreateModel(
            name='CustomPaymentProcessor',
            fields=[
                ('paymentprocessor_ptr', models.OneToOneField(auto_created=True, primary_key=True, to='shoop.PaymentProcessor', parent_link=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.paymentprocessor',),
        ),
        migrations.AlterUniqueTogether(
            name='serviceprovidertranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='payment_processor',
            field=models.ForeignKey(null=True, verbose_name='payment processor', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='shoop.PaymentProcessor'),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='carrier',
            field=models.ForeignKey(null=True, verbose_name='carrier', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='shoop.Carrier'),
        ),
    ]
