# Generated by Django 3.2.13 on 2022-06-24 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_alter_order_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.CharField(choices=[(None, 'Новый заказ'), ('NEW', 'Новый заказ'), ('CONFIRMED', 'Заказ одобрен, ожидание курьера'), ('RECEIVING', 'Курьер в пути'), ('PICKED', 'Курьер забрал заказ'), ('EXECUTING', 'Выполнение заказа'), ('DONE', 'Заказ выполнен'), ('WAITING_FOR_DELIVERY', 'Ожидание доставки'), ('DELIVERING', 'Курьер в процессе отгрузки'), ('COMPLETED', 'Заказ выполнен'), ('CANCELED', 'Заказ отменен')], default='NEW', max_length=50, verbose_name='Статус'),
        ),
    ]
