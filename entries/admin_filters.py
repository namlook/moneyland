#!/usr/bin/python3

import datetime
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Sum, F

from .models import Entry


class MonthListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('month')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'date__month'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        months = [i.month for i in Entry.objects.dates('date', 'month')]
        months = list(dict.fromkeys(months).keys())
        months_index = [
            ('1', _('janvier')), ('2', _('février')), ('3', _('mars')),
            ('4', _('avril')), ('5', _('mai')), ('6', _('juin')),
            ('7', _('juillet')), ('8', _('août')), ('9', _('septembre')),
            ('10', _('octobre')), ('11', _('novembre')), ('12', _('décembre'))
        ]
        for month in months:
            yield months_index[month]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        month = self.value()
        if month:
            month = int(month)
            return queryset.filter(
                date__gte="2016-{}-1".format(month),
                date__lt="2016-{}-1".format(month + 1))
        return queryset


class YearListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('year')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'date__year'

    def lookups(self, request, model_admin):
        current_year = datetime.date.today().year
        qs = model_admin.get_queryset(request)
        dates = Entry.objects.dates('date', 'year')
        for date in dates:
            # year = current_year - i
            # if qs.filter(date__gte="{}-1-1".format(year),
            # date__lt="{}-1-1".format(year + 1)).exists():
            # yield (year, year)
            yield (date.year, date.year)

    def queryset(self, request, queryset):
        year = self.value()
        if year:
            year = int(year)
            return queryset.filter(
                date__gte="{}-1-1".format(year),
                date__lt="{}-1-1".format(year + 1))
        return queryset


class NumPeopleListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('# people')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = '_num_people'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        elements = [
            i.num_people
            for i in qs.annotate(num_people=Count(
                "for_people", distinct=True))
        ]
        unique_elements = list(dict.fromkeys(elements).keys())
        for item in unique_elements:  # unique
            yield (str(item), _(str(item)))

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            value = int(value)
            return queryset.annotate(num_people=Count('for_people__username', distinct=True)) \
                    .filter(num_people=value)
        return queryset


class CategoryListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Categories')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'categories'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        #.filter(*filters) \
        categories = Category.objects \
            .annotate(paid_amount=Sum(F('entry__amount')/F('entry___num_people'))) \
            .order_by('-paid_amount').all()
        for category in categories:
            yield (
                category.id,
                # _("{} ({}€)".format( category.title, str(round(category.paid_amount, 2))))
                category.title)

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            value = int(value)
            return queryset.filter(categories=value)
        return queryset