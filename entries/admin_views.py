
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Sum, F

from entries.models import Entry

import json

class ReportingView(ListView):
    model = Entry
    template_name = "admin/reporting.html"
    entry_admin = None

    def get_queryset(self):
        qs = super().get_queryset()
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        if month:
            qs = qs.filter(date__month=month)
        if year:
            qs = qs.filter(date__year=year)
        return qs

    def get_total_amount(self):
        """
            * sum de paid_amount
            * sum des paid_amount des entries paid_by: "nico" beneficiary: "nath"
            * sum des paid_amount des entries paid_by: "nath" beneficiary : "nico"
        """
        self.balance = round(sum(i.paid_amount for i in self.object_list.all()), 2) # XXX

        qs = self.object_list.annotate(paid_amount=F('amount')/F('_num_people'))

        total = round(qs.aggregate(total=Sum('paid_amount'))['total'], 2)
        nath_owe_nico = round(
            qs.filter(paid_by__username="nico", for_people__username="nath") \
              .aggregate(nath_owe_nico=Sum('paid_amount'))['nath_owe_nico']
        )
        nico_owe_nath = round(
            qs.filter(paid_by__username="nath", for_people__username="nico") \
              .aggregate(nico_owe_nath=Sum('paid_amount'))['nico_owe_nath']
        )
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
        return json.dumps({
            "chart": {
                "plotBackgroundColor": None,
                "plotBorderWidth": None,
                "plotShadow": False,
                "type": 'pie'
            },
            "title": {
                "text": 'Browser market shares January, 2015 to May, 2015'
            },
            "tooltip": {
                "pointFormat": '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            "series": [{
                "name": 'Brands',
                "colorByPoint": True,
                "data": [{
                    "name": 'Microsoft Internet Explorer',
                    "y": 56.33
                }, {
                    "name": 'Chrome',
                    "y": 24.03,
                    "sliced": True,
                    "selected": True
                }, {
                    "name": 'Firefox',
                    "y": 10.38
                }, {
                    "name": 'Safari',
                    "y": 4.77
                }, {
                    "name": 'Opera',
                    "y": 0.91
                }, {
                    "name": 'Proprietary or Undetectable',
                    "y": 0.2
                }]
            }]
        })

    def get_context_data(self, **kwargs):
        context = super(ReportingView, self).get_context_data(**kwargs)
        context.update(self.entry_admin.changelist_view(self.request).context_data)
        context['now'] = timezone.now()
        context['charts_options'] = self.charts_options()
        context.update(self.get_total_amount())
        return context
