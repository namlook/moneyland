# import datetime

import json

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User
from django.db.models import Count, Sum, F, Q
# from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# from .admin_views import ReportingView
from .models import (Profile, Account, Entry, Supplier, Category,
                     ParentCategory, Expense, Income)
from .forms import EntryForm

# from .filters import YearListFilter, MonthListFilter, NumPeopleListFilter


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# def make_expense_for(username):
#     user = User.objects.filter(username=username).first()

#     def _make_expense_for(modeladmin, request, queryset):
#         for expense in queryset:
#             expense.for_people.clear()
#             expense.for_people.add(user)
#     _make_expense_for.short_description = 'marquer comme dépenses de {}'.format(user.username)
#     return _make_expense_for


class RelatedOnlyFieldListFilter(admin.RelatedFieldListFilter):
    include_empty_choice = True

    def field_choices(self, field, request, model_admin):
        qs = model_admin.get_queryset(request)
        pk_qs = qs.values_list(
            '%s__pk' % self.field_path, flat=True).distinct()
        choices = field.get_choices(
            include_blank=False, limit_choices_to={'pk__in': pk_qs})
        return choices


class EntryTypeListFilter(admin.SimpleListFilter):
    title = _('type')
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('expenses', _('expenses')),
            ('incomes', _('incomes')), )

    def queryset(self, request, queryset):
        if self.value() == 'expenses':
            return queryset.filter(amount__lt=0)
        elif self.value() == 'incomes':
            return queryset.filter(amount__gt=0)


class DonutChart(object):
    def __init__(self, title, data, drilldown_data=()):
        self.config = {
            "chart": {
                "plotBackgroundColor": None,
                "plotBorderWidth": None,
                "plotShadow": False,
                "type": 'pie'
            },
            "title": {
                "text": title
            },
            "tooltip": {
                "pointFormat": '{point.name}: <b>{point.y:.1f}€</b>'
            },
            'plotOptions': {
                'pie': {
                    'allowPointSelect': True,
                    'cursor': 'pointer',
                    'dataLabels': {
                        'enabled': False
                    },
                    'showInLegend': True
                }
            },
            "series": [{
                "name": title,
                "colorByPoint": True,
                "data": data
            }],
        }
        if drilldown_data:
            self.config['drilldown'] = {'series': drilldown_data}

    def to_json_config(self):
        return json.dumps(self.config)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    list_display = (
        'payment_type',
        'label',
        'value_date',
        'amount',
        'parent_category',
        'category',
        'paid_by',
        'for_who',
        'num_people', )
    list_select_related = (
        'category',
        'category__parent',
        'supplier',
        'paid_by', )
    filter_vertical = ('for_people', )
    date_hierarchy = 'value_date'
    actions = (
        'sep',
        'make_common_expense',
        'make_expense_for_nath',
        'make_expense_for_nico', )
    list_filter = (
        EntryTypeListFilter,
        ('paid_by', RelatedOnlyFieldListFilter),
        ('for_people', RelatedOnlyFieldListFilter),
        'num_people',
        ('category__parent', RelatedOnlyFieldListFilter),
        ('category', RelatedOnlyFieldListFilter),
        ('supplier', RelatedOnlyFieldListFilter),
        'payment_type', )
    search_fields = (
        'label',
        'category__parent__title',
        'category__title', )

    def make_common_expense(self, request, queryset):
        nath = User.objects.filter(username='nath').first()
        nico = User.objects.filter(username='nico').first()
        for expense in queryset:
            expense.for_people.clear()
            expense.for_people.add(nico, nath)

    make_common_expense.short_description = 'Marquer comme dépense commune'

    def make_expense_for_nath(self, request, queryset):
        nath = User.objects.filter(username='nath').first()
        for expense in queryset:
            expense.for_people.clear()
            expense.for_people.add(nath)

    make_expense_for_nath.short_description = 'Marquer comme dépense de Nath'

    def make_expense_for_nico(self, request, queryset):
        nico = User.objects.filter(username='nico').first()
        for expense in queryset:
            expense.for_people.clear()
            expense.for_people.add(nico)

    make_expense_for_nico.short_description = 'Marquer comme dépense de Nico'

    def sep(self):
        pass

    sep.short_description = '----'

    def get_orderfields(self, request):
        fieldnames = []
        order = request.GET.get('o')
        orders = order if type(order) is list else [order]
        for order in orders:
            descending = ''
            if order[0] == '-':
                descending = '-'
                order = order[1:]
            fieldnames.append(descending + self.list_display[int(order)])
        return fieldnames

    def get_filter(self, request):
        filters = {}
        for filter, value in request.GET.items():
            if filter in ['o', 'q']:
                continue
            filters[filter] = request.GET.get(filter)
        return filters

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        filters = self.get_filter(request)
        try:
            qs = qs.filter(**filters)
        except Exception as err:
            print('xxx', err)
            pass
        ordering = self.get_orderfields(request)
        qs = qs.order_by(*ordering)
        return qs.prefetch_related('for_people')

    def for_who(self, obj):
        return ", ".join(sorted(i.username for i in obj.for_people.all()))

    for_who.short_description = 'for'

    def parent_category(self, obj):
        return obj.category.parent

    parent_category.short_description = 'parent category'

    def save_model(self, request, obj, form, change):
        obj.account = request.user.account
        return super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        qs = self.get_queryset(request)

        total = round(qs.aggregate(total=Sum('amount'))['total'] or 0, 2)
        extra_context['total'] = total

        qs = qs.annotate(paid_amount=F('amount') / F('num_people'))

        unit_total = round(
            qs.aggregate(total=Sum('paid_amount'))['total'] or 0, 2)
        extra_context['unit_total'] = unit_total

        nath_owe_nico = qs.filter(
            paid_by__username="nico", for_people__username="nath").aggregate(
                nath_owe_nico=Sum('paid_amount'))['nath_owe_nico'] or 0

        if nath_owe_nico:
            nath_owe_nico = round(-nath_owe_nico, 2)

        nico_owe_nath = qs.filter(
            paid_by__username="nath", for_people__username="nico").aggregate(
                nico_owe_nath=Sum('paid_amount'))['nico_owe_nath'] or 0

        if nico_owe_nath:
            nico_owe_nath = round(-nico_owe_nath, 2)

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

        extra_context['nath_owe_nico'] = nath_owe_nico
        extra_context['nico_owe_nath'] = nico_owe_nath
        extra_context['final_owe_person'] = final_owe_person
        extra_context['final_owe_other_person'] = final_owe_other_person
        extra_context['final_owe_amount'] = final_owe_amount

        # categories_chart_options = self._get_categories_chart_options(request)
        # extra_context['categories_chart_options'] = categories_chart_options
        parent_categories_chart_options = self._get_parent_categories_chart_options(
            request)
        extra_context[
            'parent_categories_chart_options'] = parent_categories_chart_options
        return super().changelist_view(request, extra_context=extra_context)

    def _get_parent_categories(self, request):
        filters = {}
        for filter, value in self.get_filter(request).items():
            if filter.startswith('category__parent__'):
                filter = filter.replace('category__parent__', '')
            elif filter.startswith('category__'):
                filter = filter.replace('category__', 'children__')
            else:
                filter = 'children__entries__{}'.format(filter)
            filters[filter] = value
        return ParentCategory.objects.filter(**filters).annotate(
            total_amount=Sum('children__entries__amount'),
            paid_amount=Sum(
                F('children__entries__amount') / F('children__entries__num_people')
            )).all()

    def _get_parent_categories_chart_options(self, request):
        categories = self._get_parent_categories(request)
        data = [{
            'name': cat.title,
            'drilldown': cat.title,
            'y': round(abs(cat.paid_amount or 0), 2),
        } for cat in categories.order_by('-total_amount')]
        drilldown_data = [{
            'name': cat.title,
            'id': cat.title,
            'data': [(i.title, round(abs(i.paid_amount or 0), 2))
                     for i in cat.children.annotate(
                         total_amount=Sum('entries__amount'),
                         paid_amount=Sum(
                             F('entries__amount') / F('entries__num_people')))]
        } for cat in categories]
        return DonutChart(
            title='Parent categories',
            data=data,
            drilldown_data=drilldown_data).to_json_config()

    # def _get_categories(self, request):
    #     filters = {}
    #     for filter, value in self.get_filter(request).items():
    #         if filter.startswith('category__'):
    #             filter = filter.replace('category__', '')
    #         else:
    #             filter = "entries__{}".format(filter)
    #         filters[filter] = value
    #     return Category.objects.filter(**filters).annotate(
    #             total_amount=Sum('entries__amount')
    #             # paid_amount=Sum(F('entries__amount')/F('entries__num_people'))
    #         ).all()

    # def _get_categories_chart_options(self, request):
    #     categories = self._get_categories(request)
    #     data = [{
    #         'name': cat.title,
    #         'y': round(abs(cat.total_amount or 0), 2)
    #     } for cat in categories.order_by('-total_amount')]
    #     return DonutChart(title='Categories', data=data).to_json_config()


admin.site.register(Expense, EntryAdmin)
admin.site.register(Income, EntryAdmin)
admin.site.register(Supplier)
admin.site.register(ParentCategory)
admin.site.register(Category)
admin.site.register(Account)

# admin.site.register(Category)
# admin.site.register(User, UserAdmin)

# class MyChangeList(ChangeList):
#
#     def get_results(self, *args, **kwargs):
#         super(MyChangeList, self).get_results(*args, **kwargs)
#         # q = self.result_list.aggregate(total=Sum('amount'))
#         # self.balance = round(sum(i.amount_by_person for i in self.results_list), 2) # XXX
#         # nath_owe_nico = sum(i.amount_by_person for i in self.result_list.filter(paid_by__username="nico", for_people__username="nath"))
#         # nico_owe_nath = sum(i.amount_by_person for i in self.result_list.filter(paid_by__username="nath", for_people__username="nico"))
#         results = list(self.result_list)
#         self.balance = round(sum(i.amount_by_person for i in results), 2) # XXX
#         nath_owe_nico = sum(i.amount_by_person for i in results if i.paid_by.username == "nico" and i.for_people.filter(username="nath").count())
#         nico_owe_nath = sum(i.amount_by_person for i in results if i.paid_by.username == "nath" and i.for_people.filter(username="nico").count())
#
#         final_owe_person = "nobody"
#         final_owe_other_person = ""
#         final_owe_amount = 0
#         if nath_owe_nico > nico_owe_nath:
#             final_owe_person = "nath"
#             final_owe_other_person = "nico"
#             final_owe_amount = nath_owe_nico - nico_owe_nath
#         elif nico_owe_nath > nath_owe_nico:
#             final_owe_person = "nico"
#             final_owe_other_person = "nath"
#             final_owe_amount = nico_owe_nath - nath_owe_nico
#
#         self.nath_owe_nico = round(nath_owe_nico, 2)
#         self.nico_owe_nath = round(nico_owe_nath, 2)
#         self.final_owe_amount = round(final_owe_amount)
#         self.final_owe_person = final_owe_person.capitalize()
#         self.final_owe_other_person = final_owe_other_person.capitalize()

# @admin.register(Entry)
# class EntryAdmin(admin.ModelAdmin):
# list_display = ('date', 'label', 'amount', 'amount_by_person', 'paid_by',
# 'num_people', 'tags')
# 'for_who', 'tags', 'num_people')
# list_filter = [
# 'date',
# YearListFilter,
# MonthListFilter,
# 'paid_by',
# NumPeopleListFilter,
# CategoryListFilter
# ]
# 'for_people', 'categories']
# exclude = ('_num_people', )
# search_fields = ['label']

# def for_who(self, obj):
#     return ", ".join(sorted(i.username for i in obj.for_people.all()))
# for_who.short_description = 'for'
#
# def tags(self, obj):
#     return ", ".join(sorted(i.label for i in obj.categories.all()))

# tags.short_description = 'categories'

# def get_queryset(self, request):
#     """Use this so we can annotate with additional info."""
#     qs = super(EntryAdmin, self).get_queryset(request)
#     return qs.annotate(num_people=Count('for_people', distinct=True))

# def get_urls(self):
#     urls = super(EntryAdmin, self).get_urls()
#     my_urls = [
#         url(r'^reporting/$',
#             ReportingView.as_view(entry_admin=self),
#             name='reporting'),
#     ]
#     return my_urls + urls

# def save_related(self, request, form, formsets, change):
#     print("saved", form.for_people, formsets, change)
#     super(EntryAdmin, self).save_related(request, form, formsets, change)

# def get_total():
#     """Retourne le montant total de tous les résultats filtrés"""
#     return qs.aggregate()
#
# def changelist_view(self, request, object_id, form_url='', extra_context=None):
#     extra_context = extra_context or {}
#     qs = super(MyModelAdmin, self).get_queryset(request)
#     extra_context['total'] = self.get_total(qs)
#     return super(MyModelAdmin, self).change_view(
#         request, object_id, form_url, extra_context=extra_context,
#     )

# from controlcenter import Dashboard, widgets, app_settings

# class ModelItemList(widgets.ItemList):
#     model = Entry
#     list_display = (app_settings.SHARP, 'label', 'amount')
#     limit_to = None
#     height = 500

# class MySingleBarChart(widgets.SinglePieChart):
#     # label and series
#     values_list = ('title', 'total')
#     # Data source
#     queryset = Category.objects.order_by('total').annotate(total=Sum("entries__amount"))
#     limit_to = 10
#     height = 500
#     width = width=widgets.LARGE

#     class Chartist:
#         options = {
#             # 'labelDirection': 'explode',
#             'labelOffset': 100,
#         }

# class MyDashboard(Dashboard):
#     widgets = (
#         ModelItemList,
#         MySingleBarChart,
#     )