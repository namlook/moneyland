import csv
import codecs
import datetime
from io import TextIOWrapper

from django.shortcuts import render
from django.views.generic import FormView

from .models import Supplier, PaymentType, ParentCategory, Category, Account, Expense, Income
from .forms import FileUploadForm


class DataDialect(csv.Dialect):
    delimiter = ";"
    quoting = csv.QUOTE_MINIMAL
    quotechar = '"'
    lineterminator = "\r\n"


def sanitize_date(date_string):
    if date_string:
        return datetime.datetime.strptime(date_string, "%d/%m/%Y").date()


def sanitize_float(value):
    if value:
        return float(value.replace(' ', '').replace(',', '.'))


def sanitize_supplier(value):
    if value:
        supplier, _ = Supplier.objects.get_or_create(title=value.title())
        return supplier


def process_label(value):
    location = None
    value_date = None
    label = None
    payment_type = None
    if 'PAIEMENT CARTE' in value:
        payment_type = PaymentType.CREDIT_CARD
        location = value.split()[3]
        label = ' '.join(value.split()[4:])
        value_date = value.split()[2]
    elif 'PRLV SEPA' in value:
        label = ' '.join(value.split()[2:])
        payment_type = PaymentType.WITHDRAWAL
    elif 'VIR SEPA' in value:
        label = ' '.join(value.split()[2:])
        payment_type = PaymentType.TRANSFERT
    elif 'VIR' in value:
        label = ' '.join(value.split()[1:])
        payment_type = PaymentType.TRANSFERT
    elif 'RETRAIT DAB' in value:
        label = ' '.join(value.split()[3:])
        value_date = value.split()[2]
        payment_type = PaymentType.DAB
    else:
        label = value
    if value_date:
        if len(value_date) == 6:  # DDMMYY
            date_format = "%d%m%y"
        elif len(value_date) == 8:  # DDMMYYYY
            date_format = "%d%m%Y"
        value_date = datetime.datetime.strptime(value_date, date_format).date()
    return {
        'payment_type': payment_type,
        'label': label.title(),
        'location': location,
        'value_date': value_date,
    }


def import_csv(user, file):
    reader = csv.DictReader(file, dialect=DataDialect())
    # reader = csv.reader(f)
    for row in reader:
        print("----------")
        # print(row)
        operation_date = sanitize_date(row['dateOp'])
        value_date = sanitize_date(row['dateVal'])
        # print('dateOp', operation_date)
        # print('dateVal', value_date)
        infos = process_label(row['label'])
        payment_type = infos['payment_type']
        location = infos['location']
        value_date = infos['value_date'] or value_date
        # print('label', label)
        parent_category, _ = ParentCategory.objects.get_or_create(
            title=row['categoryParent'])
        # print('categoryParent', parent_category)
        category, _ = Category.objects.get_or_create(
            title=row['category'], parent=parent_category)
        # print('category', category)
        supplier = sanitize_supplier(row['supplierFound'])
        label = infos['label']
        if supplier and supplier.title != label:
            label = '{} ({})'.format(supplier.title, label)
        # print('supplierFound', supplier)
        amount = sanitize_float(row['amount'])
        # print('amount', amount)
        account, _ = Account.objects.get_or_create(
            number=row['accountNum'],
            label=row['accountLabel'] + ' DE NICO',
            user=user)
        # print(account)
        EntryModel = Expense
        if amount > 0:
            EntryModel = Income
        entry, _ = EntryModel.objects.get_or_create(
            operation_date=operation_date,
            value_date=value_date,
            label=label,
            category=category,
            supplier=supplier,
            amount=amount,
            account=account,
            payment_type=payment_type,
            location=location, )
        from pprint import pprint
        pprint(entry.__dict__)
        entry.for_people.add(user)


class ImportView(FormView):
    form_class = FileUploadForm
    template_name = 'admin/import.html'
    success_url = '/admin/entries/entry'

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = TextIOWrapper(
                form.cleaned_data['uploaded_file'].file, encoding='iso8859')
            try:
                import_csv(request.user, file)
                return self.form_valid(form)
            except:
                return self.form_invalid(form)


# class ImportClientsView(View):
#     '''
#     Import Prospect from csv file
#     Columns: company_name, address, zipcode, city, phone, email, web

#     Industry:
#     ('1', u'Opticien'),
#     ('2', u'Pharmacien'),
#     ('3', u'Restaurant'),
#     ('4', u'Beauté'),
#     ('5', u'Mode'),
#     ('6', u'Garage'),
#     ('0', u'Autre'),

#     '''

#     form_class = FileUploadForm
#     template_name = 'clients/admin/prospects-file-upload.html'

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = form.cleaned_data['uploaded_file']

#             def clean_upper(x):
#                 return x.upper()

#             def clean_lower(x):
#                 return x.lower()

#             def clean_zip(x):
#                 if len(str(x)) > 5:
#                     return '00000'
#                 return x.zfill(5)

#             def clean_phone(x):
#                 # remove all extra characters/separators
#                 phone = re.sub('[./ -]', '', x)
#                 # remove international prefix (+33 or 0033)
#                 phone = '0%s' % phone[-9:]
#                 return phone.zfill(10)

#             for encoding in ('utf-8', 'mac-roman'):
#                 try:
#                     prospects_df = pandas.read_csv(
#                         uploaded_file,
#                         sep=';',
#                         encoding=encoding,
#                         dtype='object',
#                         converters={
#                             'company_name': clean_upper,
#                             'zipcode': clean_zip,
#                             'phone': clean_phone,
#                             'address': clean_upper,
#                             'city': clean_upper,
#                             'email': clean_lower,
#                             'web': clean_lower
#                         })
#                     break
#                 except UnicodeDecodeError:
#                     uploaded_file.seek(0)

#             imported_count = 0
#             not_imported_lines = []
#             updated_lines = []

#             # create objects
#             for i, row in prospects_df.iterrows():
#                 row = defaultdict(lambda: None, row)
#                 try:
#                     company, created = Company.objects.get_or_create(
#                         phone=row['phone'],
#                         defaults={
#                             'name': row['company_name'],
#                             'address': row['address'],
#                             'zipcode': row['zipcode'],
#                             'city': row['city'],
#                             'phone': row['phone'],
#                             'email': row['email'],
#                             'web': row['web'],
#                             'industry': row['industry'],
#                             'buying_group':
#                             BuyingGroup.objects.get(pk=row['buying_group'])
#                             if pandas.notnull(row['buying_group']) else None,
#                             'country': Country.objects.get(name='France'),
#                             'comments': row['comments']
#                         })
#                     if created:
#                         imported_count += 1

#                         def get_title(x):
#                             if x is not None:
#                                 x = x.lower()
#                             if x in ('monsieur', 'm', 'm.', 'mr', 'homme'):
#                                 return '3'
#                             elif x in ('madame', 'mademoiselle', 'mme', 'mle',
#                                        'mlle', 'femme'):
#                                 return '2'
#                             else:
#                                 return None

#                         if pandas.notnull(row['first_name']) or pandas.notnull(
#                                 row['last_name']) or pandas.notnull(row[
#                                     'email']):
#                             Contact.objects.create(
#                                 company=company,
#                                 title=get_title(row['gender']),
#                                 first_name=row['first_name']
#                                 if pandas.notnull(row['first_name']) else '',
#                                 last_name=row['last_name']
#                                 if pandas.notnull(row['last_name']) else '',
#                                 email=row['email']
#                                 if pandas.notnull(row['email']) else '',
#                                 phone=row['mobile']
#                                 if pandas.notnull(row['mobile']) else '')
#                     else:
#                         if not company.address:
#                             company.address = row['address']
#                         if not company.zipcode:
#                             company.zipcode = row['zipcode']
#                         if not company.city:
#                             company.city = row['city']
#                         if not company.phone:
#                             company.phone = row['phone']
#                         if not company.email:
#                             company.email = row['email']
#                         if not company.industry:
#                             company.industry = row['industry']
#                         company.save()
#                         updated_lines.append(
#                             i + 2)  # i+2 to skip header and be 1 based
#                 except Company.MultipleObjectsReturned:
#                     not_imported_lines.append(i + 2)

#             self.get_success_url()

#         return render(request, self.template_name, {
#             'form': form,
#             'imported_count': imported_count,
#             'not_imported_lines': not_imported_lines,
#             'not_imported_count': len(not_imported_lines),
#             'updated_lines': updated_lines,
#             'updated_count': len(updated_lines)
#         })

#     def get_success_url(self):
#         messages.success(self.request, u'Le fichier a été téléchargé.')
#         return reverse('admin:clients_company_changelist')