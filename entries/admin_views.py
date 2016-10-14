
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Sum, F, Q

from entries.models import Entry, Category

import json

class ReportingView(ListView):
    model = Entry
    template_name = "admin/reporting.html"
    entry_admin = None # the Entry ModelAdmin

    def get_queryset(self):
        qs = super().get_queryset()
        filter_names = list(self.request.GET)
        for filter_name in filter_names:
            if filter_name == 'q':
                continue
            filter = {}
            value = self.request.GET.get(filter_name)
            if value:
                filter[filter_name] = value
                qs = qs.filter(**filter)

        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(title__contains=search)
        return qs

    def get_categories(self):
        filters = []
        filter_names = list(self.request.GET)
        for filter_name in filter_names:
            if filter_name == 'q':
                continue
            filter = {}
            value = self.request.GET.get(filter_name)
            if value:
                filter['entry__'+filter_name] = value
                filters.append(Q(**filter))

        return Category.objects \
            .annotate(paid_amount=Sum(F('entry__amount')/F('entry___num_people'))) \
            .filter(*filters).order_by('-paid_amount').all()

    def get_summary(self):
        """
            * sum de paid_amount
            * sum des paid_amount des entries paid_by: "nico" beneficiary: "nath"
            * sum des paid_amount des entries paid_by: "nath" beneficiary : "nico"
        """
        self.balance = round(sum(i.paid_amount for i in self.object_list.all()), 2) # XXX

        qs = self.object_list.annotate(paid_amount=F('amount')/F('_num_people'))

        total = round(qs.aggregate(total=Sum('paid_amount'))['total'], 2)

        nath_owe_nico = qs.filter(paid_by__username="nico", for_people__username="nath") \
              .aggregate(nath_owe_nico=Sum('paid_amount'))['nath_owe_nico'] or 0

        if nath_owe_nico:
            nath_owe_nico = round(nath_owe_nico, 2)

        nico_owe_nath = qs.filter(paid_by__username="nath", for_people__username="nico") \
          .aggregate(nico_owe_nath=Sum('paid_amount'))['nico_owe_nath'] or 0

        if nico_owe_nath:
            nico_owe_nath = round(nico_owe_nath, 2)

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

        return {
            'total': total,
            'nath_owe_nico': nath_owe_nico,
            'nico_owe_nath': nico_owe_nath,
            'final_owe_amount': final_owe_amount,
            'final_owe_other_person': final_owe_other_person,
            'final_owe_amount': final_owe_amount
        }

    def charts_options(self):
        data = [{'name': cat.title, 'y': round(cat.paid_amount, 2)} for cat in self.get_categories()]
        return json.dumps({
            "chart": {
                "plotBackgroundColor": None,
                "plotBorderWidth": None,
                "plotShadow": False,
                "type": 'pie'
            },
            "title": {
                "text": 'Categories'
            },
            "tooltip": {
                "pointFormat": '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            "series": [{
                "name": 'Categories',
                "colorByPoint": True,
                "data": data
            }]
        })

    def get_context_data(self, **kwargs):
        context = super(ReportingView, self).get_context_data(**kwargs)
        context.update(self.entry_admin.changelist_view(self.request).context_data)
        context['now'] = timezone.now()
        context['charts_options'] = self.charts_options()
        context.update(self.get_summary())
        return context
