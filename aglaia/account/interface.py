import re
from django.core.exceptions import *
from django import forms
from django.contrib.auth.models import User, Permission
from django.db.utils import *
from account.models import *
from log.interface import *


class FormatInvalidError(Exception):
	pass


class UserDoesNotExistError(Exception):
	pass


username_regex = '''[0-9A-Za-z]{6,20}'''
password_regex = '''.{6,20}'''
tel_regex = '''[0-9]{0,30}'''
school_regex = '''[0-9]{8,15}'''


def create_department(depart_name):
	depart = Department.objects.all().filter(depart_name=depart_name)
	if (len(depart) == 0):
		new_depart = Department(depart_name=depart_name)
		new_depart.save()
		return new_depart
	return depart[0]


def check_style(pattern, text):
	regex = re.compile(pattern)
	rst = regex.search(text)
	if (rst is None):
		return False
	if (rst.start() != 0 or rst.end() != len(text)):
		return False
	return True


def check_email_style(text):
	try:
		forms.EmailField().clean(text)
		return True
	except ValidationError:
		return False


def create_user(user_list):
	''' input:      a list of new account info dictionaries.
		output:     a list of new accounts.'''
	new_account = []
	user_name = ''
	password = ''
	email = ''
	tel = ''
	school_id = ''
	user = None
	type = 'none'

	for account in user_list:
		try:
			user_name = account["user_name"]  # user_name
			if (not check_style(username_regex, user_name)):
				raise FormatInvalidError("Format of user name is invalid")

			password = account["password"]  # password
			if (not check_style(password_regex, password)):
				raise FormatInvalidError("Format of password is invalid")

			tel = account['tel']  # telephone number
			if (not check_style(tel_regex, tel)):
				raise FormatInvalidError(
					"Format of telephone number is invalid")


			school_id = account['school_id']
			if (not check_style(school_regex, school_id)):
				raise FormatInvalidError(
					"Format of school_id is invalid")

			email = account["email"]  # email
			if not check_email_style(email):
				raise TypeError('email type wrong')
		except KeyError:
			raise KeyError("key content missing or wrong")
		except TypeError:
			raise TypeError("value type wrong")
		except ValueError:
			raise ValueError("value wrong")
		# create user
		try:
			user = User.objects.create_user(
				username=user_name, password=password, email=email)
		except IntegrityError:
			raise IntegrityError(
				"the user name has existed, please choose another one")
		except TypeError:
			raise TypeError("value type wrong")
		try:
			real_name = account['real_name']
			if (len(real_name) > 50):
				raise FormatInvalidError("Format of real name is invalid")

			depart_name_list = account['department']
			depart_list = []
			for depart_name in depart_name_list:
				depart = create_department(depart_name)
				depart_list.append(depart)
			status = account['status']
			account = Account(
				real_name=real_name, tel=tel,
				status=status, user=user,type=type, school_id=school_id)
			account.save()
			for depart in depart_list:
				account.department.add(depart)
			account.save()
			new_account.append(account)
		except KeyError:
			raise KeyError("key content missing or wrong")
		except TypeError:
			raise TypeError("value type wrong")
		except ValueError:
			raise ValueError("value wrong")

	return new_account


def find_users(filt, exclude):
	correct_keys = ['user_name', 'real_name', 'email',
					'password', 'department', 'tel',
					'status', 'permission', 'school_id']
	for key in filt.keys():
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)
	for key in exclude.keys():
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)

	q = Account.objects.all()
	try:
		# filter
		if 'user_name' in filt:
			q = q.filter(user__username=filt['user_name'])
		if 'real_name' in filt:
			q = q.filter(real_name=filt['real_name'])
		if 'email' in filt:
			q = q.filter(user__email=filt['email'])
		if 'type' in filt:
			q = q.filter(user__email=filt['type'])
		if 'department' in filt:
			depart_list = filt['department']
			for depart_name in depart_list:
				q = q.filter(department__depart_name=depart_name)
		if 'tel' in filt:
			q = q.filter(tel=filt['tel'])
		if 'status' in filt:
			q = q.filter(status=filt['status'])
		if 'school_id' in filt:
			q = q.filter(school_id=filt['school_id'])
		# exclude
		if 'user_name' in exclude:
			q = q.exclude(user__username=exclude['user_name'])
		if 'real_name' in exclude:
			q = q.exclude(real_name=exclude['real_name'])
		if 'email' in exclude:
			q = q.exclude(user__email=exclude['email'])
		if 'type' in exclude:
			q = q.exclude(user__email=exclude['type'])
		if 'department' in exclude:
			depart_list = exclude['department']
			for depart_name in depart_list:
				q = q.exclude(department__depart_name=depart_name)
		if 'tel' in exclude:
			q = q.exclude(tel=exclude['tel'])
		if 'status' in exclude:
			q = q.exclude(status=exclude['status'])
		if 'school_id' in exclude:
			q = q.exclude(school_id=exclude['school_id'])

		result = list(q)
		filt_perm = []
		exclude_perm = []
		if 'permission' in filt:
			filt_perm = filt['permission']
		if 'permission' in exclude:
			exclude_perm = exclude['permission']
		delete_user = []
		for account in result:
			perms = list(account.user.get_all_permissions())
			if (len(perms) == 0 and len(filt_perm) > 0):
				delete_user.append(account)
			for i in range(0, len(perms)):
				perms[i] = perms[i][perms[i].find('.') + 1:]
				if ((not (perms[i] in filt_perm) and len(filt_perm) > 0)) or (perms[i] in exclude_perm):
					delete_user.append(account)
					break

		for account in delete_user:
			result.remove(account)
		return result

	except KeyError(e):
		raise KeyError("The key is wrong")


def update_user(account_id, update_content):
	if 'id' in update_content or 'user_name' in update_content:
		raise IntegrityError(
			"id and username isn't allowed to be modified")
	correct_keys = ['real_name', 'email', 'status',
					'password', 'department', 'tel',
					'school_id','type']
	for key in update_content.keys():
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)

	account = None
	try:
		account = Account.objects.get(id=account_id)
	except:
		raise UserDoesNotExistError("Invalid ID")
	try:
		if 'real_name' in update_content:
			real_name = update_content['real_name']
			if (len(real_name) > 50):
				raise FormatInvalidError("Format of real name is invalid")
			account.real_name = real_name
		if 'email' in update_content:
			email = update_content['email']
			f = forms.EmailField()
			try:
				f.clean(email)
			except ValidationError:
				raise FormatInvalidError("Format of email is invalid")
			account.user.email = email
		if 'password' in update_content:
			password = update_content['password']
			if (not check_style(password_regex, password)):
				raise FormatInvalidError("Format of password is invalid")
			account.user.set_password(password)
		if 'school_id' in update_content:
			school_id = update_content['school_id']
			if (not check_style(school_regex, school_id)):
				raise FormatInvalidError("Format of school id is invalid")
			account.school_id = update_content['school_id']
		if 'type' in update_content:
			account.type = update_content['type']
		if 'department' in update_content:
			account.department.clear()
			for depart_name in update_content['department']:
				account.department.add(create_department(depart_name))
		if 'status' in update_content:
			account.status = update_content['status']
		if 'tel' in update_content:
			tel = update_content['tel']  # telephone number
			if (not check_style(tel_regex, tel)):
				raise FormatInvalidError(
					"Format of telephone number is invalid")
			account.tel = tel
		account.user.save()
		account.save()
		return account

	except KeyError:
		raise KeyError("key content missing or wrong")
	except TypeError:
		raise TypeError("value type wrong")
	except ValueError:
		raise ValueError("value wrong")


def delete_user(account_id):
	account = None
	try:
		account = Account.objects.get(id=account_id)
	except:
		raise UserDoesNotExistError("user don't exist")
	account.delete()
	account.user.delete()
	return True


def packed_create_user(request, *args, **kwargs):
	desc = ''
	if 'log' in kwargs:
		desc = kwargs.pop('log')
	ret = create_user(*args, **kwargs)
	for account in ret:
		create_log('user', user_id=account.user.id,
				   target=account, action='create account',
				   description=desc)
	return ret


def packed_find_users(request, *args, **kwargs):
	return find_users(*args, **kwargs)


def packed_update_user(request, *args, **kwargs):
	desc = None
	if 'log' in kwargs:
		desc = kwargs.pop('log')
	elif len(args) < 2:
		desc = kwargs['update_content']
	else:
		desc = args[1]
	ret = update_user(*args, **kwargs)
	create_log('user', user_id=request.user.id,
			   target=ret, action='change account',
			   description=desc)
	return ret


def packed_delete_user(request, *args, **kwargs):
	return delete_user(*args, **kwargs)
