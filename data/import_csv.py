import os, sys

proj_path = os.path.abspath('.')
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moneyland.settings.dev")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import csv
import codecs
import datetime

from entries.models import Account, User, Supplier, Category, ParentCategory, PaymentType, Expense, Income

# def old_import(filename):
#     with open(filename) as f:
#         reader = csv.reader(f)
#         for row in reader:
#             if row[0] == "id" or row[0].startswith("Count"):
#                 pass
#             else:
#                 id, date, title, amount, forPeople, _, paid_by, tags, _ = row
#                 paid_by = paid_by.lower().strip()
#                 user, _ = models.User.objects.get_or_create(
#                     username=paid_by, password=paid_by)
#                 entry, _ = models.Entry.objects.get_or_create(
#                     date=datetime.datetime.strptime(date, "%d/%m/%Y").date(),
#                     title=title,
#                     amount=amount,
#                     paid_by=user, )

#                 for login in forPeople.lower().split(', '):
#                     if login.strip():
#                         person, _ = models.User.objects.get_or_create(
#                             username=login, password=login)
#                         entry.for_people.add(person)

#                 for category in tags.lower().split(', '):
#                     if category.strip():
#                         category, _ = models.Category.objects.get_or_create(
#                             title=category)
#                         entry.categories.add(category)

# old_import("./data/depenses.csv")


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


def import_csv(filename):
    nico, _ = User.objects.get_or_create(username='nico')
    with codecs.open(filename, 'r', 'iso8859') as f:
        reader = csv.DictReader(f, dialect=DataDialect())
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
                user=nico)
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
                location=location,)
            from pprint import pprint
            pprint(entry.__dict__)
            entry.for_people.add(nico)


import_csv('./data/depenses.csv')