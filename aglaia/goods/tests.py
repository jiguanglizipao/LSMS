from django.test import *
from django.contrib.auth.models import *

from django.shortcuts import render, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from aglaia import settings

from goods.models import *
from account.models import *

from account.interface import *
from goods.interface import *

from account.views import *
from goods.views import *

import json

sep = "!!$$@#@#"


class TestTestCase(TestCase):

    def setUp(self):
        name1 = 'test1'
        pro_names1 = ['a', 'b', 'c', 'd']
        create_gtype(name1, pro_names1)
        name2 = 'test2'
        pro_names2 = ['aa', 'bb', 'cc', 'dd']
        create_gtype(name2, pro_names2)

        gtype1 = GType.objects.get(id=1)
        gtype2 = GType.objects.get(id=2)
        values1 = ['A', 'B', 'C', 'D']
        values2 = ['AA', 'BB', 'CC', 'DD']
        create_goods('goods1', gtype1, values1)
        create_goods('goods2', gtype2, values2)

        create_single(Goods.objects.get(id=1), ['g1', 'g2'], 'av', 'rongyu')
        create_single(Goods.objects.get(id=2), ['g3', 'g4'], 'un', 'yurong')

        account1 = {'user_name': 'rongyu', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['a lab', 'b lab'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        account = create_user([account1])
        create_borrow(account[0], 'g2', 'ba', 'hello world')
        create_borrow(account[0], 'g3', 'rej', 'a+b problem')

    def test_gtype_create_success(self):
        gtype = GType.objects.get(id=1)
        self.assertEqual(gtype.name, 'test1')
        self.assertEqual(gtype.pro_names, 'a,b,c,d,')
        gtype = GType.objects.get(id=2)
        self.assertEqual(gtype.name, 'test2')
        self.assertEqual(gtype.pro_names, 'aa,bb,cc,dd,')

    def test_gtype_find_gtypes(self):
        gtype = find_gtypes('test1')
        self.assertEqual(len(gtype), 1)
        gtype = find_gtypes('test2')
        self.assertEqual(len(gtype), 1)
        gtype = find_gtypes('test3')
        self.assertEqual(len(gtype), 0)

    def test_gtype_test_success(self):
        self.assertEqual(delete_gtype('test1'), True)
        self.assertEqual(len(GType.objects.all()), 1)

    def test_gtype_test_fail(self):
        self.assertRaises(GTypeDoesNotExistError, delete_gtype, 'test3')
        self.assertEqual(len(GType.objects.all()), 2)

    def test_gtype_set_proname_success(self):
        gtype = GType.objects.get(id=1)
        gtype.set_proname(0, 'A')
        gtype = GType.objects.get(id=1)
        self.assertEqual(gtype.pro_names, 'A,b,c,d,')
        gtype = GType.objects.get(id=1)
        gtype.set_proname(3, 'D')
        gtype = GType.objects.get(id=1)
        self.assertEqual(gtype.pro_names, 'A,b,c,D,')

    def test_gtype_set_proname_fail(self):
        gtype = GType.objects.get(id=1)
        self.assertRaises(ProNameIndexError, gtype.set_proname, 4, 'a')
        self.assertRaises(ProNameIndexError, gtype.set_proname, -1, 'a')

    def test_gtype_add_proname(self):
        gtype = GType.objects.get(id=2)
        gtype.add_proname('ee')
        gtype = GType.objects.get(id=2)
        self.assertEqual(gtype.pro_names, 'aa,bb,cc,dd,ee,')

    def test_gtype_remove_proname(self):
        gtype = GType.objects.get(id=1)
        gtype.remove_proname(0)
        gtype = GType.objects.get(id=1)
        self.assertEqual(gtype.pro_names, 'b,c,d,')

    def test_gtype_get_proname(self):
        gtype = GType.objects.get(id=1)
        self.assertEqual(gtype.get_proname(0), 'a')
        self.assertEqual(gtype.get_proname(1), 'b')
        self.assertEqual(gtype.get_proname(2), 'c')
        self.assertEqual(gtype.get_proname(3), 'd')

    def test_gtype_get_pro_index(self):
        gtype = GType.objects.get(id=2)
        self.assertEqual(gtype.get_pro_index('aa'), 0)
        self.assertEqual(gtype.get_pro_index('bb'), 1)
        self.assertEqual(gtype.get_pro_index('cc'), 2)
        self.assertEqual(gtype.get_pro_index('dd'), 3)
        self.assertEqual(gtype.get_pro_index('ee'), -1)

    def test_gtype_get_all_pros(self):
        gtype = GType.objects.get(id=1)
        name = gtype.get_all_pros()
        self.assertEqual(len(name), 4)
        self.assertEqual(name[0], 'a')
        self.assertEqual(name[1], 'b')
        self.assertEqual(name[2], 'c')
        self.assertEqual(name[3], 'd')

    def test_gtype_get_pronum(self):
        gtype = GType.objects.get(id=1)
        self.assertEqual(gtype.get_pronum(), 4)

    def test_goods_create(self):
        goods1 = Goods.objects.get(id=1)
        goods2 = Goods.objects.get(id=2)
        self.assertEqual(goods1.name, 'goods1')
        self.assertEqual(goods1.gtype, GType.objects.get(id=1))
        self.assertEqual(
            goods1.pro_values, 'A' + sep + 'B' + sep + 'C' + sep + 'D' + sep)
        self.assertEqual(goods2.name, 'goods2')
        self.assertEqual(goods2.gtype, GType.objects.get(id=2))
        self.assertEqual(
            goods2.pro_values,
            'AA' +
            sep +
            'BB' +
            sep +
            'CC' +
            sep +
            'DD' +
            sep)

    def test_goods_find(self):
        filt = {'gtype_name': 'test1', 'name': 'goods1'}
        self.assertEqual(len(find_goods(filt)), 1)
        filt = {'gtype_name': 'test2', 'name': 'goods2'}
        self.assertEqual(len(find_goods(filt)), 1)
        filt = {'gtype_name': 'test1', 'name': 'goods2'}
        self.assertEqual(len(find_goods(filt)), 0)

    def test_goods_find_keyError(self):
        filt = {'gtype': 'test1', 'name': 'goods1'}
        self.assertRaises(KeyError, find_goods, filt)

    def test_goods_delete(self):
        self.assertEqual(delete_goods(1), True)
        self.assertEqual(len(Goods.objects.all()), 1)
        self.assertRaises(GoodsDoesNotExistError, delete_goods, 1)

    def test_goods_get_pro(self):
        goods1 = Goods.objects.get(id=1)
        self.assertEqual(goods1.get_pro(0), 'A')
        self.assertEqual(goods1.get_pro(1), 'B')
        self.assertEqual(goods1.get_pro(2), 'C')
        self.assertEqual(goods1.get_pro(3), 'D')
        goods2 = Goods.objects.get(id=2)
        self.assertEqual(goods2.get_pro(0), 'AA')
        self.assertEqual(goods2.get_pro(1), 'BB')
        self.assertEqual(goods2.get_pro(2), 'CC')
        self.assertEqual(goods2.get_pro(3), 'DD')

    def test_goods_set_pro(self):
        goods1 = Goods.objects.get(id=1)
        goods1.set_pro(0, 'Aa')
        goods1 = Goods.objects.get(id=1)
        self.assertEqual(
            goods1.pro_values, 'Aa' + sep + 'B' + sep + 'C' + sep + 'D' + sep)
        goods1.set_pro(3, 'Dd')
        goods1 = Goods.objects.get(id=1)
        self.assertEqual(
            goods1.pro_values, 'Aa' + sep + 'B' + sep + 'C' + sep + 'Dd' + sep)

    def test_goods_remove_pro(self):
        goods1 = Goods.objects.get(id=1)
        goods1.remove_pro(1)
        self.assertEqual(goods1.pro_values, 'A' + sep + 'C' + sep + 'D' + sep)

    def test_single_create(self):
        single = Single.objects.get(id=1)
        self.assertEqual(single.goods, Goods.objects.get(id=1))
        self.assertEqual(single.sn, 'g1')
        self.assertEqual(single.status, 'av')
        self.assertEqual(single.user_name, 'rongyu')
        self.assertEqual(single.note, '')
        single = Single.objects.get(id=4)
        self.assertEqual(single.goods, Goods.objects.get(id=2))
        self.assertEqual(single.sn, 'g4')
        self.assertEqual(single.status, 'un')
        self.assertEqual(single.user_name, 'yurong')
        self.assertEqual(single.note, '')

    def test_single_update(self):
        update_content = {'status': 'st', "user_name": 'ry',
                                          'note': 'I am not happy'}
        update_single(1, update_content)
        single = Single.objects.get(id=1)
        self.assertEqual(single.status, 'st')
        self.assertEqual(single.user_name, 'ry')
        self.assertEqual(single.note, 'I am not happy')

    def test_single_delete(self):
        self.assertEqual(delete_single(1), True)
        self.assertEqual(len(Single.objects.all()), 3)
        self.assertRaises(SingleDoesNotExistError, delete_single, 1)
        self.assertRaises(SingleDoesNotExistError, delete_single, 5)
        self.assertRaises(SingleDoesNotExistError, delete_single, -1)

    def test_borrow_create(self):
        borrow = Borrow.objects.get(id=1)
        self.assertEqual(borrow.single.id, Single.objects.get(id=2).id)
        self.assertEqual(borrow.status, 'ba')
        self.assertEqual(borrow.note, 'hello world')
        self.assertEqual(borrow.account, Account.objects.get(id=1))
        borrow = Borrow.objects.get(id=2)
        self.assertEqual(borrow.single, Single.objects.get(id=3))
        self.assertEqual(borrow.status, 'rej')
        self.assertEqual(borrow.note, 'a+b problem')
        self.assertEqual(borrow.account, Account.objects.get(id=1))

    def test_borrow_find_filt(self):
        exclude = {}
        filt = {'single': Single.objects.get(
                id=2), 'status': 'ba', 'account': Account.objects.get(id=1)}
        self.assertEqual(len(find_borrow(filt, exclude)), 1)
        filt = {'single': Single.objects.get(id=3), 'status': 'rej'}
        self.assertEqual(len(find_borrow(filt, exclude)), 1)
        filt = {'single': Single.objects.get(id=2), 'status': 'bb'}
        self.assertEqual(len(find_borrow(filt, exclude)), 0)
        filt = {'single': Single.objects.get(id=4), 'status': 'ba'}
        self.assertEqual(len(find_borrow(filt, exclude)), 0)

    def test_borrow_find_exclude(self):
        filt = {}
        exclude = {'single': Single.objects.get(id=2), 'status': 'ba'}
        self.assertEqual(len(find_borrow(filt, exclude)), 1)
        exclude = {'single': Single.objects.get(id=3), 'status': 'rej'}
        self.assertEqual(len(find_borrow(filt, exclude)), 1)
        exclude = {'single': Single.objects.get(id=2), 'status': 'rej'}
        self.assertEqual(len(find_borrow(filt, exclude)), 0)
        exclude = {'single': Single.objects.get(id=4), 'status': 'bb'}
        self.assertEqual(len(find_borrow(filt, exclude)), 2)
        exclude = {'account': Account.objects.get(id=1)}
        self.assertEqual(len(find_borrow(filt, exclude)), 0)

    def test_borrow_find_combination(self):
        filt = {'single': Single.objects.get(id=2)}
        exclude = {'status': 'bb'}
        self.assertEqual(len(find_borrow(filt, exclude)), 1)
        filt = {'single': Single.objects.get(id=2)}
        exclude = {'status': 'ba'}
        self.assertEqual(len(find_borrow(filt, exclude)), 0)

    def test_borrow_update(self):
        update_content = {
            'status': 'aa', 'note': 'what'}
        borrow1 = update_borrow(1, update_content)
        borrow2 = Borrow.objects.get(id=1)
        self.assertEqual(borrow1.status, 'aa')
        self.assertEqual(borrow2.note, 'what')

    def test_borrow_delete_success(self):
        self.assertEqual(delete_borrow(1), True)
        self.assertEqual(len(Borrow.objects.all()), 1)

    def test_borrow_delete_fail(self):
        self.assertRaises(BorrowDoesNotExistError, delete_borrow, 3)
        self.assertRaises(BorrowDoesNotExistError, delete_borrow, -1)


class ViewTestCase(TestCase):

    def setUp(self):
        supuser = {'user_name': 'superuser', 'password': '123456',
                   'email': 'lihaoda9@163.com',
                   'real_name': 'lhd', 'department': [],
                   'tel': '12345678', 'type': 'supervisor',
                   'status': status_authed_key, 'school_id': '0123456789'}

        manager = {'user_name': 'manager', 'password': '123456',
                   'email': 'lihaoda9@163.com', 'type': 'manager',
                   'real_name': 'lhd', 'department': [],
                   'tel': '12345678',
                   'status': status_authed_key, 'school_id': '0123456789'}
        normal = {'user_name': 'normal', 'password': '123456',
                  'email': 'lihaoda9@163.com', 'type': 'normal',
                  'real_name': 'lhd', 'department': [],
                  'tel': '12345678',
                  'status': status_authed_key, 'school_id': '0123456789'}

        accounts = create_user([supuser, manager, normal])

        accounts[1].user.user_permissions.add(
            Permission.objects.get(codename="goods_auth"))

        accounts[2].user.user_permissions.add(
            Permission.objects.get(codename="normal"))

        settings.SEND_MAIL_NOTIFY = False

        name1 = 'test1'
        pro_names1 = ['a', 'b', 'c', 'd']
        values1 = ['A', 'B', 'C', 'D']

        self.t1 = create_gtype(name1, pro_names1)
        self.g1 = create_goods('goods1', self.t1, values1)
        ss = create_single(self.g1, ['sn1', 'sn2'], 'av', 'rongyu')
        self.s1 = ss[0]
        self.s2 = ss[1]

        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        self.b1 = create_borrow(accounts[2], 'sn1', 'ba', message.tostring())

    # -------- show_manage ---------
    def assertIsMessage(self, resp, message):
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'message.html')
        self.assertIn('message', resp.context)
        self.assertEqual(resp.context['message'], message)

    def test_add_goods(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        type_name = 'gtype1'
        prosname = ['pro1', 'pro2', 'pro3', 'pro4']

        gname = 'add_goods_gn1'
        wrong_gname = '123'

        gpros = ['p1', 'p2', 'p3', 'p4']
        sns = 'ssn1,ssn2,ssn3,,ssn4,,,ssn5'
        snss = sns.split(',')

        create_gtype(type_name, prosname)

        dic = {}
        dic['name'] = gname
        dic['type_name'] = type_name
        dic['sn'] = sns

        for i in range(0, len(gpros)):
            dic['pro' + str(i + 1) + '_value'] = gpros[i]

        correct = self.manager.post(reverse('goods.views.add_goods'), dic)
        self.assertRedirects(correct, reverse('goods.views.show_list'))

        sgls = Single.objects.filter(goods__name=gname)
        self.assertEqual(len(sgls), 5)
        for s in sgls:
            self.assertIn(s.sn, snss)

        dic['type_name'] = wrong_gname
        wgname = self.manager.post(reverse('goods.views.add_goods'),
                                   dic)
        self.assertIsMessage(wgname, 'Add goods failed: No Such Goods Type')

        dic.pop('name')

        noname = self.manager.post(reverse('goods.views.add_goods'),
                                   dic)
        self.assertIsMessage(noname, 'Key not found: "\'name\'"')

    def test_do_type_props(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        type_name = 'gtype1'
        prosname = ['pro1', 'pro2', 'pro3', 'pro4']

        wrong_gname = 'wrong'

        create_gtype(type_name, prosname)

        dic = {}
        dic['type_name'] = type_name

        correct = self.manager.post(reverse('goods.views.do_type_props'), dic)
        self.assertEqual(correct.status_code, 200)

        self.assertJSONEqual(
            correct.content.decode(),
            json.dumps({'pro_names': prosname})
        )

        dic['type_name'] = wrong_gname
        wgname = self.manager.post(reverse('goods.views.do_type_props'),
                                   dic)
        self.assertEqual(wgname.status_code, 200)
        self.assertJSONEqual(
            wgname.content.decode(),
            json.dumps({'pro_names': []})
        )

        dic.pop('type_name')

        noname = self.manager.post(reverse('goods.views.do_type_props'),
                                   dic)
        self.assertIsMessage(noname, 'Find goods type failed: "\'type_name\'"')

    def test_add_type(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        type_name = 'gtype1'
        prosname = ['pro1', 'pro2', 'pro3', 'pro4']

        dic = {}
        dic['type_name'] = type_name

        nopro = self.manager.post(reverse('goods.views.add_type'), dic)
        self.assertIsMessage(
            nopro, 'Some thing Wrong While adding type: No Type contrib Added!')

        for i in range(0, len(prosname)):
            dic['pro' + str(i + 1) + '_name'] = prosname[i]

        correct = self.manager.post(reverse('goods.views.add_type'), dic)
        self.assertRedirects(correct, reverse('goods.views.show_add_goods'))

        pros = GType.objects.get(name=type_name).get_all_pros()
        self.assertListEqual(pros, prosname)

        exist = self.manager.post(reverse('goods.views.add_type'), dic)
        self.assertIsMessage(
            exist, 'Some thing Wrong While adding type: type name exist!')

    def test_do_accept_borrow(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': BORROW_AUTHING_KEY})
        update_single(self.s1.id, {'status': AVALIABLE_KEY})

        note = 'testnote'

        dic = {}
        dic['id'] = self.b1.id

        nonote = self.manager.post(
            reverse('goods.views.do_accept_borrow'), dic)
        self.assertIsMessage(nonote, 'Accept borrow failed: "\'note\'"')

        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_accept_borrow'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, ACCEPTED_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        update_borrow(self.b1.id, {'status': BORROW_AUTHING_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_accept_borrow'),
            dic
        )
        self.assertIsMessage(wrong_sgl, 'The good is not avaliable!')

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        wrong_sgl = self.manager.post(
            reverse('goods.views.do_accept_borrow'),
            dic
        )
        self.assertIsMessage(wrong_sgl, 'This Request is not under verifying!')

    def test_do_reject_borrow(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': BORROW_AUTHING_KEY})
        update_single(self.s1.id, {'status': AVALIABLE_KEY})

        note = 'testnote'

        dic = {}
        dic['id'] = self.b1.id

        nonote = self.manager.post(
            reverse('goods.views.do_reject_borrow'), dic)
        self.assertIsMessage(nonote,
                             'Reject borrow failed: "\'note\'"')

        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_reject_borrow'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, REJECTED_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_reject_borrow'),
            dic
        )
        self.assertIsMessage(wrong_sgl, 'This Request is not under verifying!')

    def test_do_finish_borrow(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': ACCEPTED_KEY})
        update_single(self.s1.id, {'status': AVALIABLE_KEY})

        dic = {}
        nonote = self.manager.post(
            reverse('goods.views.do_finish_borrow'), dic)
        self.assertIsMessage(nonote, 'Finish borrow failed: "\'id\'"')

        dic['id'] = self.b1.id

        correct = self.manager.post(
            reverse('goods.views.do_finish_borrow'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, BORROWED_KEY)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, BORROWED_KEY)

        update_borrow(self.b1.id, {'status': BORROW_AUTHING_KEY})
        wrong_brw = self.manager.post(
            reverse('goods.views.do_finish_borrow'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not accepted!')

        update_borrow(self.b1.id, {'status': ACCEPTED_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_finish_borrow'),
            dic
        )
        self.assertIsMessage(wrong_sgl, 'The good is not avaliable!')

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, BORROW_AUTHING_KEY)

    def test_do_accept_return(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': RETURN_AUTHING_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        nonote = self.manager.post(
            reverse('goods.views.do_accept_return'), dic)
        self.assertIsMessage(nonote, 'Accept return failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        dic['lost'] = 'false'
        correct = self.manager.post(
            reverse('goods.views.do_accept_return'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, RETURN_PENDING_KEY)

        update_borrow(self.b1.id, {'status': RETURN_AUTHING_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic['lost'] = 'true'
        correct = self.manager.post(
            reverse('goods.views.do_accept_return'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, LOST_KEY)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, LOST_KEY)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_accept_return'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a return auth status!')

        update_borrow(self.b1.id, {'status': RETURN_AUTHING_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_accept_return'),
            dic
        )
        self.assertIsMessage(
            wrong_sgl, 'The good is not in a borrowed status!')

    def test_do_finish_return(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': RETURN_PENDING_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        nonote = self.manager.post(
            reverse('goods.views.do_finish_return'),
            dic)
        self.assertIsMessage(nonote, 'Finish return failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id

        dic['intact'] = 'true'
        correct = self.manager.post(
            reverse('goods.views.do_finish_return'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, RETURNED_KEY)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, AVALIABLE_KEY)

        update_borrow(self.b1.id, {'status': RETURN_PENDING_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic['intact'] = 'false'
        correct = self.manager.post(
            reverse('goods.views.do_finish_return'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, DAMAGED_KEY)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, UNAVALIABLE_KEY)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_finish_return'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not accepted to return!')

        update_borrow(self.b1.id, {'status': RETURN_PENDING_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_finish_return'),
            dic
        )
        self.assertIsMessage(
            wrong_sgl, 'The good is not in a borrowed status!')

    def test_do_accept_repair(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': REPAIR_APPLY_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.manager.post(
            reverse('goods.views.do_accept_repair'),
            dic)
        self.assertIsMessage(noid,
                             'Accept Repair failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_accept_repair'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, REPAIR_PEND_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_accept_repair'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a repair apply status!')

        update_borrow(self.b1.id, {'status': REPAIR_APPLY_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_accept_repair'),
            dic
        )
        self.assertIsMessage(
            wrong_sgl, 'The good is not in a borrowed status!')

    def test_do_reject_repair(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': REPAIR_APPLY_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.manager.post(
            reverse('goods.views.do_reject_repair'),
            dic)
        self.assertIsMessage(noid,
                             'Reject Repair failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_reject_repair'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, BORROWED_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_reject_repair'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a repair apply status!')

        update_borrow(self.b1.id, {'status': REPAIR_APPLY_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_reject_repair'),
            dic
        )
        self.assertIsMessage(
            wrong_sgl, 'The good is not in a borrowed status!')

    def test_do_start_repair(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': REPAIR_PEND_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.manager.post(
            reverse('goods.views.do_start_repair'),
            dic)
        self.assertIsMessage(noid,
                             'Start Repair failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_start_repair'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, REPAIRING_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, REPAIRING_KEY)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_start_repair'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a repair pend status!')

        update_borrow(self.b1.id, {'status': REPAIR_PEND_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_start_repair'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a borrowed status!')

    def test_do_finish_repair(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': REPAIRING_KEY})
        update_single(self.s1.id, {'status': REPAIRING_KEY})

        dic = {}
        noid = self.manager.post(
            reverse('goods.views.do_finish_repair'),
            dic)
        self.assertIsMessage(noid,
                             'Finish Repair failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_finish_repair'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, FINISH_REPAIR_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, REPAIRING_KEY)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_finish_repair'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a repairing status!')

        update_borrow(self.b1.id, {'status': REPAIRING_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_finish_repair'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a repairing status!')

    def test_do_return_repair(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': FINISH_REPAIR_KEY})
        update_single(self.s1.id, {'status': REPAIRING_KEY})

        dic = {}
        noid = self.manager.post(
            reverse('goods.views.do_return_repair'),
            dic)
        self.assertIsMessage(noid,
                             'Return Repair failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_return_repair'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, BORROWED_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, BORROWED_KEY)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_return_repair'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a finish repair status!')

        update_borrow(self.b1.id, {'status': FINISH_REPAIR_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_return_repair'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a repairing status!')

    # ----------- show list --------------
    def test_do_set_unavailable(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_single(self.s1.id, {'status': AVALIABLE_KEY})

        dic = {}

        noid = self.manager.post(
            reverse('goods.views.do_set_unavailable'),
            dic)
        self.assertIsMessage(noid,
                             'Set single good unavailable failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.s1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_set_unavailable'),
            dic
        )
        self.assertRedirects(correct,
                             reverse('goods.views.show_list'))
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, UNAVALIABLE_KEY)
        self.assertEqual(s2.note, note)

        correct = self.manager.post(
            reverse('goods.views.do_set_unavailable'),
            dic
        )
        self.assertIsMessage(correct,
                             'The goods cannot be set to unavailable!')

    def test_do_set_available(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_single(self.s1.id, {'status': UNAVALIABLE_KEY})

        dic = {}

        noid = self.manager.post(
            reverse('goods.views.do_set_available'),
            dic)
        self.assertIsMessage(noid,
                             'Set single good available failed: "\'id\'"')

        dic['id'] = self.s1.id

        correct = self.manager.post(
            reverse('goods.views.do_set_available'),
            dic
        )
        self.assertRedirects(correct,
                             reverse('goods.views.show_list'))
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, AVALIABLE_KEY)

        correct = self.manager.post(
            reverse('goods.views.do_set_available'),
            dic
        )
        self.assertIsMessage(correct,
                             'The goods cannot be set to available!')

    def test_do_destroy(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_single(self.s1.id, {'status': UNAVALIABLE_KEY})

        dic = {}

        noid = self.manager.post(
            reverse('goods.views.do_destroy'),
            dic)
        self.assertIsMessage(noid,
                             'Set single good destroyed failed: "\'id\'"')

        dic['id'] = self.s1.id

        correct = self.manager.post(
            reverse('goods.views.do_destroy'),
            dic
        )
        self.assertRedirects(correct,
                             reverse('goods.views.show_list'))
        s2 = Single.objects.get(id=self.s1.id)
        self.assertEqual(s2.status, DESTROYED_KEY)
    # --------- show_borrow -----------

    def test_do_borrow(self):
        self.normal = Client()
        self.assertTrue(
            self.normal.login(username='normal', password='123456'))

        update_single(self.s2.id, {'status': AVALIABLE_KEY})

        dic = {}

        noid = self.normal.post(
            reverse('goods.views.do_borrow'),
            dic)
        self.assertIsMessage(noid,
                             'Borrow request failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.s2.id
        dic['note'] = note

        correct = self.normal.post(
            reverse('goods.views.do_borrow'),
            dic
        )
        self.assertRedirects(correct,
                             reverse('goods.views.show_borrow'))

        brw = Borrow.objects.get(single=self.s2)
        self.assertEqual(brw.account.user.username, 'normal')
        self.assertEqual(brw.status, BORROW_AUTHING_KEY)
        self.assertEqual(Message(brw.note).last()['text'], note)

        update_single(self.s2.id, {'status': UNAVALIABLE_KEY})
        correct = self.normal.post(
            reverse('goods.views.do_borrow'),
            dic
        )
        self.assertIsMessage(correct,
                             'The good is not avaliable!')

    def test_do_return_goods(self):
        self.normal = Client()
        self.assertTrue(
            self.normal.login(username='normal', password='123456'))

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.normal.post(
            reverse('goods.views.do_return_goods'),
            dic)
        self.assertIsMessage(noid,
                             'Return request failed: "\'id\'"')

        dic['id'] = self.b1.id

        correct = self.normal.post(
            reverse('goods.views.do_return_goods'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, RETURN_AUTHING_KEY)
        self.assertEqual(Message(b2.note).last()['text'], USER_RETURN_MESSAGE)

        wrong_brw = self.normal.post(
            reverse('goods.views.do_return_goods'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a borrowed status!')

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.normal.post(
            reverse('goods.views.do_return_goods'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a borrowed status!')

    def test_do_miss_goods(self):
        self.normal = Client()
        self.assertTrue(
            self.normal.login(username='normal', password='123456'))

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.normal.post(
            reverse('goods.views.do_miss_goods'),
            dic)
        self.assertIsMessage(noid,
                             'Miss request failed: "\'id\'"')

        dic['id'] = self.b1.id

        correct = self.normal.post(
            reverse('goods.views.do_miss_goods'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, RETURN_AUTHING_KEY)
        self.assertEqual(Message(b2.note).last()['text'], USER_MISS_MESSAGE)

        wrong_brw = self.normal.post(
            reverse('goods.views.do_miss_goods'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a borrowed status!')

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.normal.post(
            reverse('goods.views.do_miss_goods'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a borrowed status!')

    def test_do_repair_goods(self):
        self.normal = Client()
        self.assertTrue(
            self.normal.login(username='normal', password='123456'))

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.normal.post(
            reverse('goods.views.do_repair_goods'),
            dic)
        self.assertIsMessage(noid,
                             'Repair apply failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.normal.post(
            reverse('goods.views.do_repair_goods'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, REPAIR_APPLY_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_brw = self.normal.post(
            reverse('goods.views.do_repair_goods'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a borrowed status!')

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.normal.post(
            reverse('goods.views.do_repair_goods'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a borrowed status!')

    #do_destroy_goods#

    def test_do_destroy_goods(self):
        self.normal = Client()
        self.assertTrue(
            self.normal.login(username='normal', password='123456'))

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.normal.post(
            reverse('goods.views.do_destroy_goods'),
            dic)
        self.assertIsMessage(noid,
                             'Destroy apply failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.normal.post(
            reverse('goods.views.do_destroy_goods'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, DESTROY_APPLY_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_brw = self.normal.post(
            reverse('goods.views.do_destroy_goods'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a borrowed status!')

        update_borrow(self.b1.id, {'status': BORROWED_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.normal.post(
            reverse('goods.views.do_destroy_goods'),
            dic
        )
        self.assertIsMessage(wrong_sgl,
                             'The good is not in a borrowed status!')

    def test_do_accept_destroy(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': DESTROY_APPLY_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.manager.post(reverse('goods.views.do_accept_destroy'), dic)
        self.assertIsMessage(noid,
                             'Accept Destroy failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_accept_destroy'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, DESTROY_ACCEPT_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_accept_destroy'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a destroy apply status!')

        update_borrow(self.b1.id, {'status': DESTROY_APPLY_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_accept_destroy'),
            dic
        )
        self.assertIsMessage(
            wrong_sgl, 'The good is not in a borrowed status!')

    def test_do_reject_destroy(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='manager', password='123456'))

        update_borrow(self.b1.id, {'status': DESTROY_APPLY_KEY})
        update_single(self.s1.id, {'status': BORROWED_KEY})

        dic = {}
        noid = self.manager.post(
            reverse('goods.views.do_reject_destroy'),
            dic)
        self.assertIsMessage(noid,
                             'Reject Destroy failed: "\'id\'"')

        note = 'testnote'
        dic['id'] = self.b1.id
        dic['note'] = note

        correct = self.manager.post(
            reverse('goods.views.do_reject_destroy'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_manage'))

        b2 = Borrow.objects.get(id=self.b1.id)
        self.assertEqual(b2.status, BORROWED_KEY)
        self.assertEqual(Message(b2.note).last()['text'], note)

        wrong_brw = self.manager.post(
            reverse('goods.views.do_reject_destroy'),
            dic
        )
        self.assertIsMessage(wrong_brw,
                             'This Request is not in a destroy apply status!')

        update_borrow(self.b1.id, {'status': DESTROY_APPLY_KEY})
        update_single(self.s1.id, {'status': LOST_KEY})

        wrong_sgl = self.manager.post(
            reverse('goods.views.do_reject_destroy'),
            dic
        )
        self.assertIsMessage(
            wrong_sgl, 'The good is not in a borrowed status!')

    #apply goods#

    def test_apply_goods(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(username='normal', password='123456'))

        type_name = 'gtype1'
        prosname = ['pro1', 'pro2', 'pro3', 'pro4']

        gname = 'add_goods_gn1'

        gpros = ['p1', 'p2', 'p3', 'p4']
        sns = 'ssn1'
        snss = sns.split(',')

        create_gtype(type_name, prosname)

        dic = {}
        dic['name'] = gname
        dic['type_name'] = type_name
        dic['ext_num'] = '1'
        dic['note'] = 'note'
        dic['sn'] = sns

        for i in range(0, len(gpros)):
            dic['pro' + str(i + 1) + '_value'] = gpros[i]

        dic['pro5_value'] = 'ext_value'
        dic['pro5_name'] = 'ext_type'

        correct = self.manager.post(reverse('goods.views.apply_goods'), dic)
        self.assertRedirects(correct, reverse('goods.views.show_list'))

        agls = Apply_Goods.objects.filter(name=gname)
        self.assertEqual(len(agls), 1)
        for s in agls:
            self.assertIn(s.sn, snss)

        dic.pop('name')

        noname = self.manager.post(reverse('goods.views.apply_goods'),
                                   dic)
        self.assertIsMessage(noname, 'Key not found: "\'name\'"')
