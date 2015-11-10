from excel.views import *
from django.test import *

from django.http import Http404, HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.contrib.auth.models import *
from django.core.urlresolvers import reverse

from aglaia import settings

from goods.models import *
from account.models import *
from computing.models import *

from account.interface import *
from goods.interface import *
from computing.interface import *

from account.views import *
from goods.views import *
from computing.views import *
import struct

sep = "!!$$@#@#"


class MessageCenterTestCase(TestCase):

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
        create_goods('goods2', gtype1, values1)
        create_goods('goods3', gtype2, values2)

        create_single(
            Goods.objects.get(
                id=1), [
                'g1', 'g3'], 'av', 'jiguanglizipao')
        create_single(Goods.objects.get(id=2), ['g2'], 'av', 'jiguanglizipao')
        create_single(
            Goods.objects.get(
                id=3), [
                'g5', 'g4'], 'un', 'jiguanglizipao')

        account = {
            'user_name': 'jiguanglizipao',
            'password': 'jiguanglizipao',
            'email': 'jiguanglizipao@jiguanglizipao.com',
            'real_name': 'jiguanglizipao',
            'department': [
                'a lab',
                'b lab'],
            'tel': '12345678',
            'status': 'test',
            'school_id': '0123456789'}
        account = create_user([account])
        create_borrow(account[0], 'g2', 'ba', 'hello world')
        create_borrow(account[0], 'g3', 'rej', 'a+b problem')

        computing1 = {
            'pc_type': 'v',
            'cpu': 'core',
            'memory': 1024,
            'disk': 100,
            'disk_type': 's',
            'os': 'windows',
            'sn': 'c1',
            'expire_time': date(
                year=2015,
                month=11,
                day=11) +
            timedelta(
                days=4),
            'login': 'jiguanglizipao',
            'password': 'jiguanglizipao',
            'status': 'vi',
            'account': Account.objects.get(
                id=1),
            'note': "what the fuck",
            'address': '127.0.0.1',
            'flag': True,
            'data_content': "I'm important",
            'name': 'comp1',
            'pack_name': 'pack1'}
        computing3 = {
            'pc_type': 'v',
            'cpu': 'core',
            'memory': 1024,
            'disk': 100,
            'disk_type': 's',
            'os': 'windows',
            'sn': 'c3',
            'expire_time': date(
                year=2015,
                month=11,
                day=11) +
            timedelta(
                days=4),
            'login': 'jiguanglizipao',
            'password': 'jiguanglizipao',
            'status': 'vi',
            'account': Account.objects.get(
                id=1),
            'note': "what the fuck",
            'address': '127.0.0.1',
            'flag': True,
            'data_content': "I'm important",
            'name': 'comp1',
            'pack_name': 'pack1'}
        computing2 = {
            'pc_type': 'r',
            'cpu': 'core',
            'memory': 1024,
            'disk': 100,
            'disk_type': 'h',
            'sn': 'c2',
            'os': 'linux',
            'expire_time': date(
                year=2015,
                month=11,
                day=11) +
            timedelta(
                days=4),
            'login': 'jiguanglizipao',
            'password': 'jiguanglizipao',
            'status': 'vf',
            'account': Account.objects.get(
                id=1),
            'note': "what the hell",
            'address': '127.0.0.2',
            'flag': False,
            'data_content': "",
            'name': 'comp2',
            'pack_name': 'pack2'}
        c = [computing1, computing2, computing3]
        create_computing(c)

        account[0].user.user_permissions.add(
            Permission.objects.get(codename="goods_auth"))

        settings.SEND_MAIL_NOTIFY = False

        apply = Apply_Goods(
            name='test',
            sn='test',
            type_name='test1',
            account=account[0],
            pro_names='Gender!!$$@#@#price!!$$@#@#',
            pro_values='Gender!!$$@#@#price!!$$@#@#')
        apply.save()

    def assertIsMessage(self, resp, message):
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'excel_message.html')
        self.assertIn('message', resp.context)
        self.assertEqual(resp.context['message'], message)

    def test_index(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        wgname = self.manager.get(reverse('excel.views.index'))
        self.assertEqual(wgname.status_code, 200)
        self.assertTemplateUsed(wgname, 'excel_index.html')

    def test_export_database(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        wgname = self.manager.get(reverse('excel.views.export_database'))
        self.assertEqual(wgname.status_code, 200)

    def test_import_database(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        wgname = self.manager.get(reverse('excel.views.export_database'))
        self.assertEqual(wgname.status_code, 200)
        string = str()
        for item in wgname.streaming_content:
            string = string + item.decode()
        file = open('excel/test.xml', 'w')
        file.write(string)
        file.close()
        wgname = self.manager.get(
            reverse('excel.views.import_database'), {
                'ran': 'test'})
        self.assertEqual(wgname.status_code, 200)
        self.assertIsMessage(wgname, 'Import Success')
        file = open('excel/test.xml', 'w')
        file.write('123123')
        file.close()
        wgname = self.manager.get(
            reverse('excel.views.import_database'), {
                'ran': 'test'})
        self.assertEqual(wgname.status_code, 200)
        self.assertIsMessage(wgname, 'Import Error File Destroyed')

    def test_export_excel(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        wgname = self.manager.get(reverse('excel.views.export_excel'))
        self.assertEqual(wgname.status_code, 200)
        file = open('excel/test.xlsx', 'wb')
        file.write(wgname.content)
        file.close()
        self.assertNotEqual(xlrd.open_workbook('excel/test.xlsx'), None)
        os.remove('excel/test.xlsx')

    def test_import_excel(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        export = self.manager.get(reverse('excel.views.export_excel'))
        self.assertEqual(export.status_code, 200)
        file = open('excel/test.xlsx', 'wb')
        file.write(export.content)
        file.close()
        wgname = self.manager.get(
            reverse('excel.views.import_excel'), {
                'ran': 'test'})
        self.assertEqual(wgname.status_code, 200)
        file = open('excel/test.xlsx', 'wb')
        file.write(export.content)
        file.close()
        comp = Computing.objects.get(id=1)
        comp.sn = 'test'
        comp.save()
        comp = Computing.objects.get(id=2)
        comp.cpu = 'INTEL'
        comp.save()
        single = Single.objects.get(id=1)
        single.sn = 'SINGLE1'
        single.save()
        single = Single.objects.get(id=2)
        single.goods.name = 'NAME123'
        single.goods.save()
        wgname = self.manager.get(
            reverse('excel.views.import_excel'), {
                'ran': 'test'})
        self.assertEqual(wgname.status_code, 200)
        self.assertTemplateUsed(wgname, 'excel_list.html')

    def test_import_goods(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        export = self.manager.get(reverse('excel.views.export_excel'))
        self.assertEqual(export.status_code, 200)
        file = open('excel/test.xlsx', 'wb')
        file.write(export.content)
        file.close()
        single = Single.objects.get(id=1)
        single.sn = 'SINGLE1'
        single.save()
        single = Single.objects.get(id=2)
        single.goods.name = 'NAME123'
        single.goods.save()
        wgname = self.manager.get(
            reverse('excel.views.import_excel'), {
                'ran': 'test'})
        self.assertEqual(wgname.status_code, 200)
        self.assertTemplateUsed(wgname, 'excel_list.html')
        for item in wgname.context['goods_list']:
            item['pro_values'] = item['values']
            confirm = self.manager.post(
                reverse('excel.views.import_goods'), item)
            self.assertEqual(confirm.status_code, 200)
            self.assertEqual(confirm.content.decode(), 'Success')

    def test_import_computing(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))

        export = self.manager.get(reverse('excel.views.export_excel'))
        self.assertEqual(export.status_code, 200)
        file = open('excel/test.xlsx', 'wb')
        file.write(export.content)
        file.close()
        comp = Computing.objects.get(id=1)
        comp.sn = 'test'
        comp.save()
        comp = Computing.objects.get(id=2)
        comp.cpu = 'INTEL'
        comp.save()
        wgname = self.manager.get(
            reverse('excel.views.import_excel'), {
                'ran': 'test'})
        self.assertEqual(wgname.status_code, 200)
        self.assertTemplateUsed(wgname, 'excel_list.html')
        for item in wgname.context['computing_list']:
            confirm = self.manager.post(
                reverse('excel.views.import_computing'), item)
            self.assertEqual(confirm.status_code, 200)
            self.assertEqual(confirm.content.decode(), 'Success')

    def test_exception(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='jiguanglizipao',
                password='jiguanglizipao'))
        exc = self.manager.post(reverse('excel.views.import_computing'), {})
        self.assertIn('Error', exc.content.decode().split(' '))
        exc = self.manager.post(reverse('excel.views.import_goods'), {})
        self.assertIn('Error', exc.content.decode().split(' '))
        self.assertRaises(
            (Exception,
             self.manager.get,
             reverse('excel.views.import_excel')))
        self.assertRaises(
            (Exception,
             self.manager.get,
             reverse('excel.views.import_database')))
