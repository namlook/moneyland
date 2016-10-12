from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Sum
import datetime

# Register your models here.

from .models import User, Category, Entry

admin.site.register(User)
admin.site.register(Category)



from django.utils.translation import ugettext_lazy as _

class MonthListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('month')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'month'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', _('janvier')),
            ('2', _('février')),
            ('3', _('mars')),
            ('4', _('avril')),
            ('5', _('mai')),
            ('6', _('juin')),
            ('7', _('juillet')),
            ('8', _('août')),
            ('9', _('septembre')),
            ('10', _('octobre')),
            ('11', _('novembre')),
            ('12', _('décembre'))
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        month = self.value()
        if month:
            month = int(month)
            return queryset.filter(date__gte="2016-{}-1".format(month),
                    date__lt="2016-{}-1".format(month + 1))
        return queryset


class YearListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('year')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'year'

    def lookups(self, request, model_admin):
        current_year = datetime.date.today().year
        qs = model_admin.get_queryset(request)
        for i in range(5):
            year = current_year - i
            if qs.filter(date__gte="{}-1-1".format(year),
                        date__lt="{}-1-1".format(year + 1)).exists():
                yield (year, year)


    def queryset(self, request, queryset):
        year = self.value()
        if year:
            year = int(year)
            return queryset.filter(date__gte="{}-1-1".format(year),
                                        date__lt="{}-1-1".format(year + 1))
        return queryset


class NumPeopleListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('# people')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'num_people'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        elements = [i.num_people for i in qs.annotate(num_people=Count("for_people", distinct=True))]
        unique_elements = list(dict.fromkeys(elements).keys())
        for item in unique_elements: # unique
            yield (str(item), _(str(item)))

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            value = int(value)
            return queryset.annotate(num_people=Count('for_people__login', distinct=True)) \
                    .filter(num_people=value)
        return queryset


class MyChangeList(ChangeList):

    def get_results(self, *args, **kwargs):
        super(MyChangeList, self).get_results(*args, **kwargs)
        # q = self.result_list.aggregate(total=Sum('amount'))
        # self.total = q['total']
        results = list(self.result_list)
        self.balance = round(sum(i.paid_amount for i in results), 2) # XXX
        # nath_owe_nico = sum(i.paid_amount for i in self.result_list.filter(paid_by__login="nico", for_people__login="nath"))
        # nico_owe_nath = sum(i.paid_amount for i in self.result_list.filter(paid_by__login="nath", for_people__login="nico"))
        nath_owe_nico = sum(i.paid_amount for i in results if i.paid_by.login == "nico" and i.for_people.filter(login="nath").count())
        nico_owe_nath = sum(i.paid_amount for i in results if i.paid_by.login == "nath" and i.for_people.filter(login="nico").count())

        final_owe_person = "nobody"
        final_owe_other_person = ""
        final_owe_amount = 0
        if nath_owe_nico > nico_owe_nath:
            final_owe_person = "nath"
            final_owe_other_person = "nico"
            final_owe_amount = nath_owe_nico - nico_owe_nath
        elif nico_owe_nath > nath_owe_nico:
            final_owe_person = "nico"
            final_owe_other_person = "nath"
            final_owe_amount = nico_owe_nath - nath_owe_nico

        self.nath_owe_nico = round(nath_owe_nico, 2)
        self.nico_owe_nath = round(nico_owe_nath, 2)
        self.final_owe_amount = round(final_owe_amount)
        self.final_owe_person = final_owe_person.capitalize()
        self.final_owe_other_person = final_owe_other_person.capitalize()




class EntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'paid_amount', 'paid_by', 'for_who', 'tags')#, 'num_people')
    list_filter = ['date', YearListFilter, MonthListFilter, 'paid_by', NumPeopleListFilter, 'for_people', 'categories']
    search_fields = ['title']

    def get_changelist(self, request):
        return MyChangeList

    def for_who(self, obj):
        return ", ".join(sorted(i.login for i in obj.for_people.all()))
    for_who.short_description = 'for'

    def tags(self, obj):
        return ", ".join(sorted(i.title for i in obj.categories.all()))
    tags.short_description = 'categories'

    def num_people(self, obj):
        """# of people sharing the amount"""
        return obj.num_people
    num_people.short_description = "# people"

    def has_video(self, obj):
        """Does the expert have a video?"""

        return obj.has_video / obj.num_companies
    has_video.short_description = "video?"

    def get_queryset(self, request):
        """Use this so we can annotate with additional info."""

        qs = super(EntryAdmin, self).get_queryset(request)
        return qs.annotate(num_people=Count('for_people', distinct=True))


admin.site.register(Entry, EntryAdmin)
