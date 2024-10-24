from django.db import models
from .quickbase_requests import fetch_activity_data

ACTIVITY_CHOICES = [
    ("", ""),
    ("from_ign", "From IGN"),
    ("from_vendor", "From Vendor"),
]

ACTIVITY_RELATED_TO_CHOICES = [
    ("", ""),
    ("internet_service", "Internet Service"),
    ("network_link", "Network Link"),
    ("pop", "POP"),
]

# Pop Database = bjvepsjqq
# Field 8 = POP ID

pop_values = fetch_activity_data(
    "bjvepsjqq", [3, 8],  where="{36.CT.'Active'}", sortby=[{"fieldId": 8, "order": "ASC"}])
internet_values = fetch_activity_data(
    "bjx5t3hbx", [3, 6], where="{31.CT.'Active'}", sortby=[{"fieldId": 6, "order": "ASC"}])
network_link_values = fetch_activity_data(
    "bjvepudtt", [3, 7], where="{38.CT.'Active'}", sortby=[{"fieldId": 7, "order": "ASC"}])
ign_eng_values = fetch_activity_data(
    "bgcihz8py", [3, 53], where="{52.CT.'Active'}", sortby=[{"fieldId": 53, "order": "ASC"}])


# pop list from quickbase para POP_ID_CHOICES
POP_ID_CHOICES = []
# create this tuples with empty values
IGN_ENG_CHOICES = [(" ", " ")]
POP_ID_CHOICES = [(" ", " ")]
INTERNET_ID_CHOICES = [(" ", " ")]
NETWORK_LINK_ID_CHOICES = [(" ", " ")]

for id, name in zip(pop_values[0], pop_values[1]):
    POP_ID_CHOICES.append((str(id), name))


for id, name in zip(internet_values[0], internet_values[1]):
    INTERNET_ID_CHOICES.append((str(id), name))


for id, name in zip(network_link_values[0], network_link_values[1]):
    NETWORK_LINK_ID_CHOICES.append((str(id), name))


for value in ign_eng_values[1]:
    if value != None:
        IGN_ENG_CHOICES.append((value['id'], value['name']))

STATUS_CHOICES = [("Not Started", "Not Started"),
                  ("dismissed", "Dismissed"), ("completed", "Completed")]


class Core(models.Model):
    id = models.AutoField(primary_key=True, unique=True, editable=False)
    activity_type = models.CharField(
        max_length=100, choices=ACTIVITY_CHOICES, default='', verbose_name="Activity Type")
    activity_related_to = models.CharField(
        max_length=100, choices=ACTIVITY_RELATED_TO_CHOICES, default='')
    ign_engineer = models.CharField(
        max_length=100, default='', choices=IGN_ENG_CHOICES, verbose_name="Ign Enginner")

    internet_id = models.CharField(
        max_length=100, default='', choices=INTERNET_ID_CHOICES)

    network_link = models.CharField(
        max_length=100, default='', choices=NETWORK_LINK_ID_CHOICES, verbose_name="Network Link")

    pop = models.CharField(
        max_length=100, default='', choices=POP_ID_CHOICES)

    status = models.CharField(
        max_length=100, default='not_started', choices=STATUS_CHOICES)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    duration = models.CharField(max_length=6, default='')
    downtime = models.TextField(
        max_length=6, default='', verbose_name="Downtime who will send to customer")
    affected_services = models.TextField(max_length=10000, default='')

    Description = models.TextField(
        max_length=100, default='', verbose_name="Core Description")
    Description_to_customers = models.TextField(
        max_length=100, default='', verbose_name="Description to customers")

    location = models.CharField(max_length=100, default='')

    remote_hands_information = models.TextField(max_length=100, default='')

    core_quickbase_id = models.CharField(
        max_length=6)
    tickets_zendesk_generated = models.TextField(max_length=1000, default='')

    zabbix_maintenance_id = models.CharField(
        max_length=6)

    def __str__(self):
        return self.activity_type


class Troubleshooting_registration(models.Model):
    core_quickbase_id = models.CharField(
        max_length=6)
    date = models.DateTimeField(auto_now_add=True)
    circuito = models.CharField(
        max_length=20)
    resultadoping = models.TextField()
    status = models.TextField()
    interfacestatus = models.TextField()
    statusquickbase = models.TextField()
