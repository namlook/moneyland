
import os, sys

proj_path = "/Users/namlook/Documents/projets/django/moneyland/"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moneyland.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()




import csv
import datetime
from entries import models

with open("./data/depenses.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0] == "id" or row[0].startswith("Count"):
            pass
        else:
            id, date, title, amount, forPeople, _, paid_by, tags, _ = row
            user, _ = models.User.objects.get_or_create(login=paid_by.lower())
            entry, _ = models.Entry.objects.get_or_create(
                date = datetime.datetime.strptime(date, "%d/%m/%Y").date(),
                title = title,
                amount = amount,
                paid_by = user,
            )

            for login in forPeople.lower().split(', '):
                if login.strip():
                    person, _ = models.User.objects.get_or_create(login=login)
                    entry.for_people.add(person)

            for category in tags.lower().split(', '):
                if category.strip():
                    category, _ = models.Category.objects.get_or_create(title=category)
                    entry.categories.add(category)
