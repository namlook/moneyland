# import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User
# from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

# from .admin_views import ReportingView
from .models import Profile, Account, Entry, User, Supplier, Category, ParentCategory, PaymentType, Expense, Income
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


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    form = EntryForm
    list_display = ('payment_type', 'label', 'value_date', 'amount',
                    'parent_category', 'category', 'num_people', 'for_who')
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
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
