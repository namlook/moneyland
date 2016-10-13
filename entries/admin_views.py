
from django.views.generic.list import ListView
from django.utils import timezone
from django.db.models import Sum

from entries.models import Entry

class ReportingView(ListView):
    model = Entry
    template_name = "admin/reporting.html"
    entry_admin = None

    def get_total_amount(self):
        return round(self.object_list.aggregate(total=Sum("amount"))['total'], 2)

    def get_context_data(self, **kwargs):
        context = super(ReportingView, self).get_context_data(**kwargs)
        context.update(self.entry_admin.changelist_view(self.request).context_data)
        context['now'] = timezone.now()
        context['total'] = self.get_total_amount()
        return context
