from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.template.defaultfilters import slugify


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class ParentCategory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = _("parent categories")

    def save(self, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
        return super().save(**kwargs)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey(ParentCategory, related_name="children")

    class Meta:
        ordering = ["title"]
        verbose_name_plural = _("categories")

    def save(self, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
        return super().save(**kwargs)

    def __str__(self):
        return self.title


class Supplier(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def save(self, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
        return super().save(**kwargs)

    def __str__(self):
        return self.title


class Account(models.Model):
    number = models.CharField(max_length=20)
    label = models.CharField(max_length=200)
    user = models.OneToOneField(User, related_name="account")

    def __str__(self):
        return "{} ({})".format(self.label, self.number)


class PaymentType(object):
    CREDIT_CARD = 'CREDITCARD'
    TRANSFERT = 'VIR'
    WITHDRAWAL = 'PRLV'
    DAB = 'DAB'
    CASH = 'CASH'

    choices = [
        (CREDIT_CARD, _('credit card')),
        (TRANSFERT, _('transfert')),
        (WITHDRAWAL, _('withdrawal')),
        (DAB, _('DAB')),
        (CASH, _('CASH')),
    ]


class Entry(models.Model):
    operation_date = models.DateField(verbose_name=_("operation date'"))
    value_date = models.DateField(verbose_name=_("value date"))
    label = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="entries")
    supplier = models.ForeignKey(
        Supplier, related_name="entries", blank=True, null=True)
    amount = models.FloatField(verbose_name=_("total amount"))
    account = models.ForeignKey(Account, related_name="entries")
    paid_by = models.ForeignKey(
        User, related_name="paid_entries", blank=True, null=True)
    for_people = models.ManyToManyField(User, related_name="entries")
    num_people = models.PositiveIntegerField(default=0)
    payment_type = models.CharField(
        verbose_name=_('payment type'),
        max_length=100,
        choices=PaymentType.choices,
        blank=True,
        null=True)
    location = models.CharField(
        verbose_name=_('location'), max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-operation_date"]
        verbose_name_plural = "entries"

    @property
    def amount_by_person(self):
        if (self.num_people > 0):
            return self.amount / self.num_people
        return 0

    def save(self, *args, **kwargs):
        if not self.operation_date:
            self.operation_date = self.value_date
        return super().save(*args, **kwargs)


class Expense(Entry):
    def save(self, *args, **kwargs):
        if self.amount > 0:  # expense should be negative
            self.amount = self.amount * -1
        return super().save(*args, **kwargs)


class Income(Entry):
    def save(self, *args, **kwargs):
        if self.amount < 0:  # income should be positive
            self.amount = self.amount * -1
        return super().save(*args, **kwargs)


@receiver(m2m_changed, sender=Entry.for_people.through)
def calculate_num_people(sender, instance, action, reverse, **kwargs):
    """ Automatically recalculate the number of people who share the amount """
    if not reverse and action in ['post_add', 'post_remove', 'post_clear']:
        obj = Entry.objects.filter(pk=instance.pk).first()
        instance.num_people = obj.for_people.count()
        # instance.amount_by_person = instance.amount / instance._num_people
        instance.save()
