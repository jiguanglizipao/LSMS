from django.core.exceptions import *
from django.db.utils import *
from django.db.models import *
from goods.models import *
from log.interface import *
from aglaia.message_center import Message

sep = "!!$$@#@#"


class GTypeDoesNotExistError(Exception):
	pass


class GoodsDoesNotExistError(Exception):
	pass


class SingleDoesNotExistError(Exception):
	pass


class BorrowDoesNotExistError(Exception):
	pass


def create_gtype(name, names):
	pro_names = ""
	for n in names:
		pro_names = pro_names + n + ','
	gtype = GType(name=name, pro_names=pro_names)
	gtype.save()
	return gtype


def find_gtypes(name):
	q = GType.objects.all()
	q = q.filter(name=name)
	return q


def delete_gtype(name):
	gtype = None
	try:
		gtype = GType.objects.get(name=name)
	except:
		raise GTypeDoesNotExistError("GType does not exist")
	gtype.delete()
	return True


def create_goods(name, gtype, values):
	pro_values = ''
	for v in values:
		pro_values += (v + sep)
	goods = Goods(name=name, gtype=gtype, pro_values=pro_values)
	goods.save()
	return goods


def find_goods(filt):
	correct_keys = ['gtype_name', 'name']
	for key in filt.keys():
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)
	q = Goods.objects.all()
	try:
		if 'gtype_name' in filt:
			q = q.filter(gtype__name=filt['gtype_name'])
		if 'name' in filt:
			q = q.filter(name=filt['name'])
		return q
	except Exception:
		raise ("Error in find goods")


def delete_goods(goods_id):
	goods = None
	try:
		goods = Goods.objects.get(id=goods_id)
	except:
		raise GoodsDoesNotExistError("Goods does not exist")
	goods.delete()
	return True


def create_single(goods, SN, status, user_name):
	new_single = []
	for sn in SN:
		if sn:
			single = Single(sn=sn, goods=goods,
							status=status, note='', user_name=user_name)
			single.save()
			new_single.append(single)
	return new_single


def update_single(single_id, update_content):
	correct_keys = ['status', 'user_name', 'note']
	for key in update_content:
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)
	single = None
	try:
		single = Single.objects.get(id=single_id)
	except:
		raise SingleDoesNotExistError("Single does not exist")
	try:
		if 'status' in update_content:
			single.status = update_content['status']
		if 'user_name' in update_content:
			single.user_name = update_content['user_name']
		if 'note' in update_content:
			single.note = update_content['note']
		single.save()
		return single
	except:
		raise Exception("Error in update single")


def delete_single(single_id):
	single = None
	try:
		single = Single.objects.get(id=single_id)
	except:
		raise SingleDoesNotExistError("Single does not exist")
	single.delete()
	return True


def create_borrow(account, sn, status, note=Message().tostring()):
	single = None
	try:
		single = Single.objects.get(sn=sn)
	except:
		raise Exception("Invalid SN number")
	try:
		borrow = Borrow(
			single=single, status=status, note=note,
			account=account)
		borrow.save()
	except:
		raise Exception("Error in borrow create")
	return borrow


def find_borrow(filt, exclude):
	correct_keys = ['single', 'status', 'account']
	for key in filt.keys():
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)

	q = Borrow.objects.all()
	try:
		if 'single' in filt:
			q = q.filter(single=filt['single'])
		if 'status' in filt:
			q = q.filter(status=filt['status'])
		if 'account' in filt:
			q = q.filter(account=filt['account'])

		if 'single' in exclude:
			q = q.exclude(single=exclude['single'])
		if 'status' in exclude:
			q = q.exclude(status=exclude['status'])
		if 'account' in exclude:
			q = q.exclude(account=exclude['account'])
		return q
	except Exception:
		raise Exception("Error in find borrow")


def update_borrow(borrow_id, update_content):
	correct_keys = ['status', 'note']
	for key in update_content:
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)
	borrow = None
	try:
		borrow = Borrow.objects.get(id=borrow_id)
	except:
		raise BorrowDoesNotExistError("Borrow does not exist")
	try:
		if 'status' in update_content:
			borrow.status = update_content['status']
		if 'note' in update_content:
			borrow.note = update_content['note']
		borrow.save()
		return borrow
	except:
		raise Exception("Error in update borrow")


def delete_borrow(borrow_id):
	borrow = None
	try:
		borrow = Borrow.objects.get(id=borrow_id)
	except:
		raise BorrowDoesNotExistError("Borrow does not exist")
	borrow.delete()
	return True


def packed_create_gtype(request, *args, **kwargs):
	return create_gtype(*args, **kwargs)


def packed_find_gtypes(request, *args, **kwargs):
	return find_gtypes(*args, **kwargs)


def packed_delete_gtype(request, *args, **kwargs):
	return delete_gtype(*args, **kwargs)


def packed_create_goods(request, *args, **kwargs):
	return create_goods(*args, **kwargs)


def packed_create_apply_goods(request, name, pro_name, pro_value, sns, status, account, note):
	pro_values = ''
	for v in pro_value:
		pro_values += (v + sep)

	pro_names = ''
	for v in pro_name:
		pro_names += (v + sep)

	for sn in sns:
		if sn:
			goods = Apply_Goods(name=name, pro_values=pro_values, pro_names=pro_names, status=status,
			                    account=account, note=note, sn=sn)
			goods.save()
			return goods


def packed_find_apply_goods(request, filt, exclude):
	correct_keys = ['status', 'account']
	for key in filt.keys():
		if not (key in correct_keys):
			raise KeyError("The key: %s is wrong", key)

	q = Apply_Goods.objects.all()
	try:
		if 'status' in filt:
			q = q.filter(status=filt['status'])
		if 'account' in filt:
			q = q.filter(account=filt['account'])

		if 'status' in exclude:
			q = q.exclude(status=exclude['status'])
		if 'account' in exclude:
			q = q.exclude(account=exclude['account'])
		return q

	except Exception:
		raise Exception("Error in find Apply Goods")


def packed_find_goods(request, *args, **kwargs):
	return find_goods(*args, **kwargs)


def packed_delete_goods(request, *args, **kwargs):
	return delete_goods(*args, **kwargs)


def packed_create_single(request, *args, **kwargs):
	desc = ''
	if 'log' in kwargs:
		desc = kwargs.pop('log')
	ret = create_single(*args, **kwargs)
	for sgl in ret:
		create_log('single', user_id=request.user.id,
				   target=sgl, action='create good',
				   description=desc)
	return ret


def packed_update_single(request, *args, **kwargs):
	desc = ''
	if 'log' in kwargs:
		desc = kwargs.pop('log')
	elif len(args) < 1:
		desc = kwargs['update_content']
	else:
		desc = args[1]
	ret = update_single(*args, **kwargs)
	create_log('single', user_id=request.user.id,
			   target=ret, action='change good',
			   description=desc)
	return ret


def packed_delete_single(request, *args, **kwargs):
	return delete_single(*args, **kwargs)


def packed_create_borrow(request, *args, **kwargs):
	desc = ''
	if 'log' in kwargs:
		desc = kwargs.pop('log')
	elif len(args) < 4:
		desc = kwargs['note']
	else:
		desc = args[3]
	ret = create_borrow(*args, **kwargs)
	create_log('borrow', user_id=request.user.id,
			   target=ret, action='create borrow',
			   description=desc)
	return ret


def packed_find_borrow(request, *args, **kwargs):
	return find_borrow(*args, **kwargs)


def packed_update_borrow(request, *args, **kwargs):
	desc = ''
	if 'log' in kwargs:
		desc = kwargs.pop('log')
	elif len(args) < 2:
		desc = kwargs['update_content']
	else:
		desc = args[1]
	ret = update_borrow(*args, **kwargs)
	create_log('borrow', user_id=request.user.id,
			   target=ret, action='update borrow',
			   description=desc)
	return ret


def packed_delete_borrow(request, *args, **kwargs):
	return delete_borrow(*args, **kwargs)
