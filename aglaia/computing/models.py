from django.db import models
from account.models import Account

PHYSICAL_MACHINE = 'real'
PHYSICAL_MACHINE_KEY = 'r'
VIRTUAL_MACHINE = 'virtual'
VIRTUAL_MACHINE_KEY = 'v'

MACHINE = 'HDD'
MACHINE_KEY = 'h'
SSD = 'SSD'
SSD_KEY = 's'

VERIFYING = 'verifying'
VERIFYING_KEY = 'vi'
VERIFY_FAIL = 'verify_fail'
VERIFY_FAIL_KEY = 'vf'
VERIFY_SUCCESS = 'verify_success'
VERIFY_SUCCESS_KEY = 'vs'
BORROWED = 'borrowed'
BORROWED_KEY = 'bo'
MODIFY_APPLY = 'modify_apply'
MODIFY_APPLY_KEY = 'ma'
# MODIFYING = 'modifying'
# MODIFYING_KEY = 'mi'
# RETURN_APPLY = 'return_apply'
# RETURN_APPLY_KEY = 'ra'
RETURNING = 'returning'
RETURNING_KEY = 'ri'
RETURNED = 'returned'
RETURNED_KEY = 'ret'
DAMAGED = 'damaged'
DAMAGED_KEY = 'dd'

BUSY_KEY = 'b'
BUSY = 'busy'
NORMAL_KEY = 'n'
NORMAL = 'normal'
DISABLE_KEY = 'd'
DISABLE = 'disable'

DESTROYING_KEY = 'di'
DESTROYING = 'destroying'
DESTROYED_KEY = 'de'
DESTROYED = 'destroyed'


class Server(models.Model):
    SERVER_CHOICES = (
        (BUSY_KEY, BUSY),
        (NORMAL_KEY, NORMAL),
        (DISABLE_KEY, DISABLE)
    )
    status = models.CharField(max_length=3, choices=SERVER_CHOICES)
    description = models.CharField(max_length=500)
    name = models.CharField(max_length=50)
    configuration = models.CharField(max_length=500)


class Computing(models.Model):
    TYPE_CHOICES = (
        (PHYSICAL_MACHINE_KEY, PHYSICAL_MACHINE),
        (VIRTUAL_MACHINE_KEY, VIRTUAL_MACHINE)
    )
    DISK_CHOICES = (
        (MACHINE_KEY, MACHINE),
        (SSD_KEY, SSD)
    )
    STATUS_CHOICES = (
        (VERIFYING_KEY, VERIFYING),
        (VERIFY_FAIL_KEY, VERIFY_FAIL),
        (VERIFY_SUCCESS_KEY, VERIFY_SUCCESS),
        (BORROWED_KEY, BORROWED),
        (MODIFY_APPLY_KEY, MODIFY_APPLY),
        (RETURNING_KEY, RETURNING),
        (RETURNED_KEY, RETURNED),
        (DAMAGED_KEY, DAMAGED)
    )
    name = models.CharField(max_length=100, blank=True)
    pack_name = models.CharField(max_length=100, blank=True)
    pc_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    cpu = models.CharField(max_length=30)
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)
    disk_type = models.CharField(max_length=3, choices=DISK_CHOICES)
    os = models.CharField(max_length=50, default='linux')
    sn = models.CharField(max_length=60, default='', unique=True)
    expire_time = models.DateField()
    login = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    account = models.ForeignKey(Account)
    note = models.CharField(max_length=500)
    address = models.CharField(max_length=30, blank=True)
    flag = models.BooleanField(default=False)
    data_content = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.sn


class Package(models.Model):
    TYPE_CHOICES = (
        (PHYSICAL_MACHINE_KEY, PHYSICAL_MACHINE),
        (VIRTUAL_MACHINE_KEY, VIRTUAL_MACHINE)
    )
    DISK_CHOICES = (
        (MACHINE_KEY, MACHINE),
        (SSD_KEY, SSD)
    )
    name = models.CharField(max_length=50)
    cpu = models.CharField(max_length=30)
    pc_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='r')
    memory = models.IntegerField(default=0)
    disk = models.IntegerField(default=0)
    disk_type = models.CharField(max_length=3, choices=DISK_CHOICES)
    os = models.CharField(max_length=50, default='linux')
