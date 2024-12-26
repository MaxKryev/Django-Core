from django.db import migrations


def insert_price_data(apps, schema_editor):
    Price = apps.get_model('img_txt_anal', 'Price')

    prices = [
        (1, 'image/png', 2),
        (2, 'image/jpeg', 3),
        (3, 'image/gif', 4),
    ]

    for id, file_type, price in prices:
        Price.objects.update_or_create(
            id=id,
            defaults={'file_type': file_type, 'price': price}
        )


class Migration(migrations.Migration):
    dependencies = [
        ('img_txt_anal', '0001_initial'),  # Зависимость от первой миграции
    ]

    operations = [
        migrations.RunPython(insert_price_data),
    ]
