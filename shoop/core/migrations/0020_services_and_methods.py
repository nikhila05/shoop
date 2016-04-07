# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import shoop.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('shoop', '0019_contact_merchant_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixedCostBehaviorComponentTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('description', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'shoop_fixedcostbehaviorcomponent_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'fixed cost behavior component Translation',
            },
        ),
        migrations.CreateModel(
            name='ServiceBehaviorComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', shoop.core.fields.InternalIdentifierField(null=True, editable=False, max_length=64, blank=True, unique=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProviderTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'managed': True,
                'db_table': 'shoop_serviceprovider_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'service provider Translation',
            },
        ),
        migrations.CreateModel(
            name='WaivingCostBehaviorComponentTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('description', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'managed': True,
                'db_table': 'shoop_waivingcostbehaviorcomponent_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'waiving cost behavior component Translation',
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
            field=models.BooleanField(default=True, verbose_name='enabled'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='shop',
            field=models.ForeignKey(verbose_name='shop', blank=True, to='shoop.Shop', null=True),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='choice_identifier',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='enabled',
            field=models.BooleanField(default=True, verbose_name='enabled'),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='shop',
            field=models.ForeignKey(verbose_name='shop', blank=True, to='shoop.Shop', null=True),
        ),
        migrations.AlterField(
            model_name='paymentmethodtranslation',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='shippingmethodtranslation',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
        migrations.CreateModel(
            name='Carrier',
            fields=[
                ('serviceprovider_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.ServiceProvider')),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.serviceprovider',),
        ),
        migrations.CreateModel(
            name='FixedCostBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.ServiceBehaviorComponent')),
                ('price_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent', models.Model),
        ),
        migrations.CreateModel(
            name='PaymentProcessor',
            fields=[
                ('serviceprovider_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.ServiceProvider')),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.serviceprovider',),
        ),
        migrations.CreateModel(
            name='WaivingCostBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.ServiceBehaviorComponent')),
                ('price_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
                ('waive_limit_value', shoop.core.fields.MoneyValueField(max_digits=36, decimal_places=9)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent', models.Model),
        ),
        migrations.CreateModel(
            name='WeightLimitsBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.ServiceBehaviorComponent')),
                ('min_weight', models.DecimalField(null=True, verbose_name='minimum weight', max_digits=36, decimal_places=6, blank=True)),
                ('max_weight', models.DecimalField(null=True, verbose_name='maximum weight', max_digits=36, decimal_places=6, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent',),
        ),
        migrations.AddField(
            model_name='serviceprovidertranslation',
            name='master',
            field=models.ForeignKey(related_name='base_translations', editable=False, to='shoop.ServiceProvider', null=True),
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_shoop.serviceprovider_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='servicebehaviorcomponent',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_shoop.servicebehaviorcomponent_set+', editable=False, to='contenttypes.ContentType', null=True),
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
                ('carrier_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.Carrier')),
            ],
            options={
                'verbose_name': 'custom carrier',
                'verbose_name_plural': 'custom carriers',
            },
            bases=('shoop.carrier',),
        ),
        migrations.CreateModel(
            name='CustomPaymentProcessor',
            fields=[
                ('paymentprocessor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='shoop.PaymentProcessor')),
            ],
            options={
                'verbose_name': 'custom payment processor',
                'verbose_name_plural': 'custom payment processors',
            },
            bases=('shoop.paymentprocessor',),
        ),
        migrations.AddField(
            model_name='waivingcostbehaviorcomponenttranslation',
            name='master',
            field=models.ForeignKey(related_name='translations', editable=False, to='shoop.WaivingCostBehaviorComponent', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='serviceprovidertranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='fixedcostbehaviorcomponenttranslation',
            name='master',
            field=models.ForeignKey(related_name='translations', editable=False, to='shoop.FixedCostBehaviorComponent', null=True),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='payment_processor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='payment processor', blank=True, to='shoop.PaymentProcessor', null=True),
        ),
        migrations.AddField(
            model_name='shippingmethod',
            name='carrier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='carrier', blank=True, to='shoop.Carrier', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='waivingcostbehaviorcomponenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='fixedcostbehaviorcomponenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
