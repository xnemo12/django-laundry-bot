from django.db import models

from arcgis.models import Arcgis
from tgbot.models import User
from utils.models import CreateUpdateTracker, nb
from django.utils.translation import gettext_lazy as _


class Order(CreateUpdateTracker):

    class OrderState(models.TextChoices):
        NEW = 'NEW', _('Новый заказ')
        CONFIRMED = 'CONFIRMED', _('Заказ одобрен, ожидание курьера')
        RECEIVING = 'RECEIVING', _('Курьер в пути')
        PICKED = 'PICKED', _('Курьер забрал заказ')
        EXECUTING = 'EXECUTING', _('Выполнение заказа')
        DONE = 'DONE', _('Заказ выполнен')
        WAITING_FOR_DELIVERY = 'WAITING_FOR_DELIVERY', _('Ожидание доставки')
        DELIVERING = 'DELIVERING', _('Курьер в процессе отгрузки')
        COMPLETED = 'COMPLETED', _('Заказ выполнен')
        CANCELLED = 'CANCELED', _('Заказ отменен')
        __empty__ = _('Новый заказ')

    user = models.ForeignKey(User, verbose_name=_('Клиент'), related_name='users', on_delete=models.CASCADE)
    courier = models.ForeignKey(User, verbose_name=_('Курьер'), related_name='couriers', on_delete=models.CASCADE, **nb)
    location = models.ForeignKey(Arcgis, verbose_name=_('Локация'), on_delete=models.CASCADE, **nb)
    order_time = models.DateTimeField(verbose_name=_('Время заказа'), **nb)
    confirmed_time = models.DateTimeField(verbose_name=_('Согласована'), **nb)
    picked_time = models.DateTimeField(verbose_name=_('Курьер забрал заказ'), **nb)
    start_time = models.DateTimeField(verbose_name=_('Начало выполнения'), **nb)
    done_time = models.DateTimeField(verbose_name=_('Сделано'), **nb)
    delivery_time = models.DateTimeField(verbose_name=_('Доставлено'), **nb)
    description = models.CharField(verbose_name=_('Информация'), max_length=500, **nb)
    comment = models.CharField(verbose_name=_('Комментарий'), max_length=500, **nb)
    state = models.CharField(verbose_name=_('Статус'), max_length=50, choices=OrderState.choices, default=OrderState.NEW)
    phone = models.CharField(verbose_name=_('Номер телефона'), max_length=20, **nb)


class OrderPhotos(CreateUpdateTracker):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    photo = models.FileField()

