from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# class User(models.Model):
#     login = models.CharField(max_length=50)
#
#     def __str__(self):
#         return self.login
#
#     def reimboursement(self, login, year, month):
#         """how much "login" owe the user for the current month of the year"""
#         login_owe_me = Entry.objects.filter(
#             paid_by__login=login,
#             for_people__login=self.login,
#             date__year=year,
#             date__month=month)
#         return sum(i.paid_amount for i in login_owe_me)


class User(AbstractUser):
    pass

class Category(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title

class Entry(models.Model):
    date = models.DateField('date')
    title = models.CharField(max_length=200)
    amount = models.FloatField()
    paid_by = models.ForeignKey(User, related_name='expenses')
    for_people = models.ManyToManyField(User, related_name='entries')
    categories = models.ManyToManyField(Category)
    _num_people = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["date"]
        verbose_name_plural = "entries"

    def __str__(self):
        return "{}[{}] - {} ({})".format(self.date, self.paid_by, self.title, self.amount)

    @property
    def paid_amount(self):
        if (self._num_people > 0):
            return self.amount / self._num_people
        return 0


from django.db.models.signals import m2m_changed
from django.dispatch import receiver

@receiver(m2m_changed, sender=Entry.for_people.through)
def calculate_num_people(sender, instance, action, **kwargs):
    """ Automatically recalculate the number of people who share the amount """
    if action == 'post_add':
        instance._num_people = instance.for_people.count()
        # instance.paid_amount = instance.amount / instance._num_people
        instance.save()
    if action == 'post_remove' or action == 'post_clear':
        instance._num_people = instance.for_people.count()
        # instance.paid_amount = instance.amount / instance._num_people
        instance.save()
