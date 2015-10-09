from django.db import models
from account.models import *
from computing.models import *
from goods.models import *
from goods.models import *


class LogAccount(models.Model):
	user_id = models.IntegerField()
	target = models.ForeignKey(Account)
	action = models.CharField(max_length=100)
	time = models.DateTimeField()
	description = models.CharField(max_length=500)

	def get_target_str(self):
		return self.target.user.username


class LogComputing(models.Model):
	user_id = models.IntegerField()
	target = models.ForeignKey(Computing)
	action = models.CharField(max_length=100)
	time = models.DateTimeField()
	description = models.CharField(max_length=500)

	def get_target_str(self):
		return self.target.name


class LogBorrow(models.Model):
	user_id = models.IntegerField()
	target = models.ForeignKey(Borrow)
	action = models.CharField(max_length=100)
	time = models.DateTimeField()
	description = models.CharField(max_length=500)

	def get_target_str(self):
		return self.target.single.sn


class LogSingle(models.Model):
	user_id = models.IntegerField()
	target = models.ForeignKey(Single)
	action = models.CharField(max_length=100)
	time = models.DateTimeField()
	description = models.CharField(max_length=500)

	def get_target_str(self):
		return self.target.sn
