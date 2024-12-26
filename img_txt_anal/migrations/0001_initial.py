import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Docs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=1000)),
                ('size', models.PositiveIntegerField(db_index=True)),
                ('external_id', models.IntegerField(blank=True, default=None, null=True)),
                ('file_type', models.CharField(default='png', max_length=30)),
            ],
            options={
                'db_table': 'docs',
            },
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(max_length=30)),
                ('price', models.FloatField()),
            ],
            options={
                'db_table': 'price',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_price', models.FloatField()),
                ('payment', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('docs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='img_txt_anal.docs')),
            ],
            options={
                'db_table': 'cart',
            },
        ),
        migrations.CreateModel(
            name='UsersToDocs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docs_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='img_txt_anal.docs')),
                ('username', models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_to_docs',
            },
        ),
    ]
