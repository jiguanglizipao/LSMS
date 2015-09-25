from django.db import models
from account.models import *

# Create your models here.
sep = "!!$$@#@#"


class ProNameIndexError(Exception):
    pass


class ProValueIndexError(Exception):
    pass


AVALIABLE_KEY = 'av'
AVALIABLE = 'available'
UNAVALIABLE_KEY = 'un'
UNAVALIABLE = 'unavailable'
BORROWED_KEY = 'bo'
BORROWED = 'borrowed'
DESTROYED_KEY = 'de'
DESTROYED = 'destroyed'
REPAIRING_KEY = 're'
REPAIRING = 'repairing'
REPAIR_APPLY_KEY = 'rpa'
REPAIR_APPLY = 'repair_applys'
REPAIR_PEND_KEY = 'repn'
REPAIR_PEND = 'repair_pend'
FINISH_REPAIR_KEY = 'fr'
FINISH_REPAIR = 'finish_repair'

BORROW_AUTHING_KEY = 'ba'
BORROW_AUTHING = 'borrow_authing'
REJECTED_KEY = 'rej'
REJECTED = 'rejected'
ACCEPTED_KEY = 'ac'
ACCEPTED = 'accepted'
RETURN_AUTHING_KEY = 'ra'
RETURN_AUTHING = 'return_authing'
RETURN_PENDING_KEY = 'rp'
RETURN_PENDING = 'return_pending'
RETURNED_KEY = 'ret'
RETURNED = 'returned'
LOST_KEY = 'lo'
LOST = 'lost'
DAMAGED_KEY = 'da'
DAMAGED = 'damaged'


class GType(models.Model):
    name = models.CharField(max_length=50)
    pro_names = models.CharField(max_length=2048)

    def __str__(self):
        return str(self.name)
    def set_proname(self, pro_id, new_name):
        names = self.pro_names.split(',')
        if(pro_id < 0 or pro_id > (len(names) - 2)):
            raise ProNameIndexError('Index Error')
        names[pro_id] = new_name
        pro_names = ""
        for i in range(0, len(names) - 1):
            pro_names = pro_names + names[i] + ','
        self.pro_names = pro_names
        self.save()

    def add_proname(self, name):
        self.pro_names = self.pro_names + name + ','
        self.save()

    def remove_proname(self, pro_id):
        names = self.pro_names.split(',')
        new_names = ''
        if(pro_id < 0 or pro_id > (len(names) - 2)):
            raise ProNameIndexError('Index Error')
        for i in range(0, len(names) - 1):
            if(i != pro_id):
                new_names = new_names + names[i] + ','
        self.pro_names = new_names
        self.save()

    def get_proname(self, pro_id):
        names = self.pro_names.split(',')
        if(pro_id < 0 or pro_id > (len(names) - 2)):
            raise ProNameIndexError('Index Error')
        return names[pro_id]

    def get_pro_index(self, pro_name):
        names = self.pro_names.split(',')
        for i in range(0, len(names) - 1):
            if(names[i] == pro_name):
                return i
        return -1

    def get_all_pros(self):
        names = self.pro_names.split(',')
        return names[0: (len(names) - 1)]

    def get_pronum(self):
        names = self.pro_names.split(',')
        return len(names) - 1


class Goods(models.Model):
    name = models.CharField(max_length=50)
    gtype = models.ForeignKey(GType)
    pro_values = models.CharField(max_length=40000)

    def __str__(self):
        return str(self.name)
    def get_pro(self, pro_id):
        values = self.pro_values.split(sep)
        return values[pro_id]

    def set_pro(self, pro_id, new_value):
        values = self.pro_values.split(sep)
        if(pro_id < 0 or pro_id > (len(values) - 2)):
            raise ProValueIndexError('Index Error')
        values[pro_id] = new_value
        pro_values = ""
        for i in range(0, len(values) - 1):
            pro_values += (values[i] + sep)
        self.pro_values = pro_values
        self.save()

    def remove_pro(self, pro_id):
        values = self.pro_values.split(sep)
        new_values = ''
        if(pro_id < 0 or pro_id > (len(values) - 2)):
            raise ProValueIndexError('Index Error')
        for i in range(0, len(values) - 1):
            if(i != pro_id):
                new_values = new_values + values[i] + sep
        self.pro_values = new_values
        self.save()


class Single(models.Model):
    STATUS_CHOICES = (
        (AVALIABLE_KEY, AVALIABLE),
        (UNAVALIABLE_KEY, UNAVALIABLE),
        (BORROWED_KEY, BORROWED),
        (DESTROYED_KEY, DESTROYED),
        (REPAIRING_KEY, REPAIRING),
        (LOST_KEY,LOST)
    )
    sn = models.CharField(max_length=60, unique=True)
    goods = models.ForeignKey(Goods, default=None)
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    user_name = models.CharField(max_length=50, default='')
    note = models.CharField(max_length=1000)
    def __str__(self):
        return str(self.goods.name) + '-' + str(self.sn)

class Borrow(models.Model):
    STATUS_CHOICES = (
        (BORROW_AUTHING_KEY, BORROW_AUTHING),
        (REJECTED_KEY, REJECTED),
        (ACCEPTED_KEY, ACCEPTED),
        (BORROWED_KEY, BORROWED),
        (REPAIR_APPLY_KEY, REPAIR_APPLY),
        (REPAIR_PEND_KEY, REPAIR_PEND),
        (REPAIRING_KEY, REPAIRING),
        (FINISH_REPAIR_KEY, FINISH_REPAIR),
        (RETURN_AUTHING_KEY, RETURN_AUTHING),
        (RETURN_PENDING_KEY, RETURN_PENDING),
        (RETURNED_KEY, RETURNED),
        (LOST_KEY, LOST),
        (DAMAGED_KEY, DAMAGED)
    )
    account = models.ForeignKey(Account, default=None)
    single = models.ForeignKey(Single)
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    user_note = models.CharField(max_length=1000)
    manager_note = models.CharField(max_length=1000)
    def __str__(self):
        return str(self.single.goods.name) + '-' + str(self.single.sn)
