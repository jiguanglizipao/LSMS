from datetime import *
from django.core.exceptions import *
from django.test import *
from computing.views import *
from computing.models import *
from computing.interface import *
from account.models import Account
from account.interface import *
from goods.views import *
from aglaia.message_center import *
from aglaia.messages import *


class TestTestCase(TestCase):

    def setUp(self):
        account = {'user_name': 'rongyu', 'password': 'rongyu',
                   'email': 'rongyu@rongy.com',
                   'real_name': 'rongyu', 'department': ['a lab', 'b lab'],
                   'tel': '12345678',
                   'status': 'test', 'school_id': '0123456789'}
        account = create_user([account])
        account[0].user.user_permissions.add(
            Permission.objects.get(codename="comput_auth"))
        account[0].user.user_permissions.add(
            Permission.objects.get(codename="normal"))
        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        computing1 = {'pc_type': 'p', 'cpu': 'core', 'memory': 1024,
                      'disk': 100, 'disk_type': 's', 'os': 'windows',
                      'sn': 'c1',
                      # hold true for 2014-11-16
                      'expire_time': date.today() + timedelta(days=4),
                      'login': 'rongyu', 'password': 'rongyu',
                      'status': 'vi', 'account': Account.objects.get(id=1),
                      'note': message.tostring(), 'address': '127.0.0.1', 'flag': 'True',
                      'data_content': "I'm important",
                      'name': 'comp1', 'pack_name': 'pack1'}
        computing2 = {'pc_type': 'p',
                      'cpu': 'core',
                      'memory': 1024,
                      'disk': 100,
                      'disk_type': 's',
                      'os': 'linux',
                      'expire_time': date.today() + timedelta(days=5),
                      'login': 'yurong',
                      'password': 'yurong',
                      'status': 'vf',
                      'account': Account.objects.get(id=1),
                      'note': message.tostring(),
                      'address': '127.0.0.2',
                      'flag': False,
                      'data_content': "",
                      'name': 'comp2',
                      'pack_name': 'pack2'}
        c = [computing1, computing2]
        create_computing(c)

        server1 = {'status': 'b', 'description': 'good',
                   'name': 'server1', 'configuration': 'good'}
        server2 = {'status': 'n', 'description': 'very good',
                   'name': 'server2', 'configuration': 'very good'}
        s = [server1, server2]
        create_server(s)

        package1 = {'cpu': 'core', 'pc_type': 'r',
                    'memory': 1024, 'disk': 1024, 'os': 'windows',
                    'disk_type': 's', 'name': 'package1'}
        package2 = {'cpu': 'xeon', 'pc_type': 'v',
                    'memory': 1025, 'disk': 1025, 'os': 'linux',
                    'disk_type': 'm', 'name': 'package2'}
        create_package(package1)
        create_package(package2)

    def test_createS_success(self):
        server = Server.objects.get(id=1)
        self.assertEqual(server.status, 'b')
        self.assertEqual(server.description, 'good')
        self.assertEqual(server.name, 'server1')
        self.assertEqual(server.configuration, 'good')
        server = Server.objects.get(id=2)
        self.assertEqual(server.status, 'n')
        self.assertEqual(server.description, 'very good')
        self.assertEqual(server.name, 'server2')
        self.assertEqual(server.configuration, 'very good')

    def test_createS_key_error(self):
        server1 = {'stat': 'b', 'description': 'good',
                           'name': 'server1', 'configuration': 'good'}
        self.assertRaises(KeyError, create_server, [server1])
        server1 = {'status': 'b', 'description': 'good',
                   'configuration': 'good'}
        self.assertRaises(KeyError, create_server, [server1])

    def test_server_filter(self):
        exclude = {}
        filt = {'status': 'b', 'description': 'good',
                'name': 'server1', 'configuration': 'good'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        filt = {'status': 'n', 'description': 'very good',
                'name': 'server2', 'configuration': 'very good'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        filt = {'status': 'n', 'description': 'good',
                'name': 'server1', 'configuration': 'good'}
        self.assertEqual(len(find_server(filt, exclude)), 0)
        filt = {'status': 'b', 'description': 'very good',
                'name': 'server1', 'configuration': 'good'}
        self.assertEqual(len(find_server(filt, exclude)), 0)

    def test_server_exclude(self):
        filt = {}
        exclude = {'status': 'b'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        exclude = {'description': 'good'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        exclude = {'name': 'server2'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        exclude = {'configuration': 'very good'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        exclude = {'status': 'b', 'name': 'server2'}
        self.assertEqual(len(find_server(filt, exclude)), 0)
        exclude = {'description': 'very good', 'configuration': 'good'}
        self.assertEqual(len(find_server(filt, exclude)), 0)
        exclude = {'status': 'f', 'name': 'server',
                   'description': 'bad', 'configuration': 'very bad'}
        self.assertEqual(len(find_server(filt, exclude)), 2)
        exclude = {'status': 't'}
        self.assertEqual(len(find_server(filt, exclude)), 2)
        exclude = {'description': 'god'}
        self.assertEqual(len(find_server(filt, exclude)), 2)
        exclude = {'name': 'sever2'}
        self.assertEqual(len(find_server(filt, exclude)), 2)
        exclude = {'configuration': 'vey good'}
        self.assertEqual(len(find_server(filt, exclude)), 2)

    def test_server_combination(self):
        filt = {'status': 'b'}
        exclude = {'name': 'server1'}
        self.assertEqual(len(find_server(filt, exclude)), 0)
        filt = {'status': 'n'}
        exclude = {'name': 'server2'}
        self.assertEqual(len(find_server(filt, exclude)), 0)
        filt = {'status': 'b'}
        exclude = {'name': 'server2'}
        self.assertEqual(len(find_server(filt, exclude)), 1)
        filt = {'status': 'n'}
        exclude = {'name': 'server4'}
        self.assertEqual(len(find_server(filt, exclude)), 1)

    def test_findS_key_error(self):
        filt = {'fuck': 1}
        self.assertRaises(KeyError, find_server, filt, {})
        exclude = {'fuck': 1}
        self.assertRaises(KeyError, find_server, {}, exclude)

    def test_updateS_success(self):
        update_content = {'status': 'd', 'description': 'hehe',
                          'name': 'server1.1', 'configuration': 'heh'}
        server1 = update_server(1, update_content)
        server2 = Server.objects.get(id=1)
        self.assertEqual(server1, server2)
        self.assertEqual(server1.status, 'd')
        self.assertEqual(server2.description, 'hehe')
        self.assertEqual(server1.name, 'server1.1')
        self.assertEqual(server2.configuration, 'heh')

    def test_updateS_invalid_ID(self):
        self.assertRaises(ServerDoesNotExistError, update_server, 10, {})

    def test_updateS_key_error(self):
        update_content = {'log': 'hehes'}
        self.assertRaises(KeyError, update_server, 1, update_content)

    def test_server_delete(self):
        self.assertEqual(delete_server(1), True)
        self.assertEqual(len(Server.objects.all()), 1)

    def test_server_delete_fail(self):
        self.assertRaises(ServerDoesNotExistError, delete_server, 10)

    def test_create_success(self):
        computing = Computing.objects.get(id=1)
        self.assertEqual(computing.pc_type, 'p')
        self.assertEqual(computing.cpu, 'core')
        self.assertEqual(computing.memory, 1024)
        self.assertEqual(computing.disk, 100)
        self.assertEqual(computing.disk_type, 's')
        self.assertEqual(computing.os, 'windows')
        # self.assertEqual(computing.sn, 'c1')
        # self.assertEqual(computing.expire_time.year, 2014)
        # self.assertEqual(computing.expire_time.month, 11)
        # self.assertEqual(computing.expire_time.day, 21)
        self.assertEqual(computing.flag, True)
        computing = Computing.objects.get(id=2)
        self.assertEqual(computing.os, 'linux')
        # self.assertEqual(computing.sn, '')
        self.assertEqual(computing.status, 'vf')
        self.assertEqual(computing.account, Account.objects.get(id=1))
        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        self.assertEqual(computing.note, message.tostring().decode())
        # self.assertEqual(computing.expire_time.year, 2014)
        # self.assertEqual(computing.expire_time.month, 11)
        # self.assertEqual(computing.expire_time.day, 22)
        self.assertEqual(computing.address, '127.0.0.2')
        self.assertEqual(computing.flag, False)

    def test_create_key_error(self):
        account = Account.objects.get(id=1)
        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        computing1 = {'pc_type': 'p', 'cpu': 'core', 'memory': 1024,
                      'disk': 100, 'disk_type': 's', 'os': 'win',
                      'expire_time': date(2014, 11, 1),
                      'logn': 'rongyu', 'password': 'rongyu',
                      'status': 'vi', 'account': account,
                      'note': message.tostring(), 'address': '127.0.0.1'}
        self.assertRaises(KeyError, create_computing, [computing1])
        account = Account.objects.get(id=1)
        computing1 = {'pc_type': 'p', 'cpu': 'core', 'memory': 1024,
                      'disk': 100, 'disk_type': 's', 'os': 'win',
                      # 'expire_time': date(2014, 11, 1),
                      'login': 'rongyu', 'password': 'rongyu',
                      'status': 'vi', 'account': account,
                      'note': message.tostring(), 'address': '127.0.0.1'}
        self.assertRaises(KeyError, create_computing, [computing1])

    def test_normal_filter(self):
        exclude = {}
        filt = {'pc_type': 'p', 'disk_type': 's',
                'account': Account.objects.get(id=1)}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'pc_type': 'p'}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'pc_type': 'p', 'disk_type': 'p',
                'account': Account.objects.get(id=1)}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'status': 'vf'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'pc_type': 'q'}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'os': 'windows'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'os': 'linux'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'os': 'mac os'}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        # filt = {'sn': 'c1'}
        # self.assertEqual(len(find_computing(filt, exclude)), 1)
        # filt = {'sn': ''}
        # self.assertEqual(len(find_computing(filt, exclude)), 1)
        # filt = {'sn': 'c2'}
        # self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'address': '127.0.0.1'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'address': '127.0.0.2'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'address': '127.0.0.3'}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'flag': False}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'flag': True, 'address': '127.0.0.2'}
        self.assertEqual(len(find_computing(filt, exclude)), 0)

    def test_normal_exclude(self):
        filt = {}
        exclude = {'pc_type': 'p', 'disk_type': 's',
                   'account': Account.objects.get(id=1)}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        exclude = {'pc_type': 'p'}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        exclude = {'status': 'vf'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'pc_type': 'q'}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        # exclude = {'sn': 'c1'}
        # self.assertEqual(len(find_computing(filt, exclude)), 1)
        # exclude = {'sn': ''}
        # self.assertEqual(len(find_computing(filt, exclude)), 1)
        # exclude = {'sn': 'c2'}
        # self.assertEqual(len(find_computing(filt, exclude)), 2)
        exclude = {'address': '127.0.0.1'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'address': '127.0.0.2'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'address': '127.0.0.3'}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        exclude = {'flag': True}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'flag': False}
        self.assertEqual(len(find_computing(filt, exclude)), 1)

    def test_time_find(self):
        exclude = {}
        filt = {'check_time': {'longer': 3}}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'check_time': {'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'check_time': {'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'check_time': {'longer': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'check_time': {'longer': 3, 'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'check_time': {'longer': 3, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'check_time': {'longer': 4, 'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'check_time': {'longer': 4, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'check_time': {'longer': 3, 'shorter': 5}}
        filt['status'] = 'vf'
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'check_time': {'longer': 3, 'shorter': 4}}
        filt['status'] = 'vf'
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'check_time': {'longer': 4, 'shorter': 5}}
        filt['status'] = 'vf'
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'check_time': {'longer': 3, 'shorter': 5}}
        filt['disk_type'] = 's'
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'check_time': {'longer': 3, 'shorter': 5}}
        filt['status'] = 'fuck'
        self.assertEqual(len(find_computing(filt, exclude)), 0)

    def test_time_exclude(self):
        filt = {}
        exclude = {'check_time': {'longer': 3}}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        exclude = {'check_time': {'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        exclude = {'check_time': {'longer': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'check_time': {'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'check_time': {'longer': 3, 'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        exclude = {'check_time': {'longer': 3, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'check_time': {'longer': 4, 'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'check_time': {'longer': 4, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        exclude = {'check_time': {'longer': 4, 'shorter': 4}}
        exclude['status'] = 'vf'
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'check_time': {'longer': 4, 'shorter': 4}}
        exclude['status'] = 'fuck'
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        exclude = {'check_time': {'longer': 4, 'shorter': 5}}
        exclude['status'] = 'vf'
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        exclude = {'check_time': {'longer': 3, 'shorter': 4}}
        filt['status'] = 'vi'
        self.assertEqual(len(find_computing(filt, exclude)), 0)

    def test_normal_combination(self):
        filt = {}
        exclude = {}
        filt['disk_type'] = 's'
        exclude['pc_type'] = 'p'
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {}
        exclude = {}
        filt['disk_type'] = 'p'
        exclude['pc_type'] = 'ffuck'
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {}
        exclude = {}
        filt['disk_type'] = 's'
        exclude['status'] = 'vi'
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {}
        exclude = {}
        filt['status'] = 'vi'
        exclude['status'] = 'fuck'
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {}
        exclude = {}
        filt['disk_type'] = 's'
        exclude['pc_type'] = 'fuck'
        self.assertEqual(len(find_computing(filt, exclude)), 2)

    def test_time_combination(self):
        filt = {'disk_type': 's', 'pc_type': 'p'}
        exclude = {'check_time': {'longer': 4, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 2)
        filt = {'disk_type': 's', 'pc_type': 'p'}
        exclude = {'check_time': {'longer': 3, 'shorter': 5}}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'disk_type': 's', 'pc_type': 'p'}
        exclude = {'check_time': {'longer': 3, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'disk_type': 's', 'status': 'vi'}
        exclude = {'check_time': {'longer': 4, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'disk_type': 's', 'status': 'vf'}
        exclude = {'check_time': {'longer': 3, 'shorter': 4}}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'disk_type': 's'}
        exclude = {'check_time': {'longer': 4, 'shorter': 4},
                   'pc_type': 'p'}
        self.assertEqual(len(find_computing(filt, exclude)), 0)
        filt = {'disk_type': 's'}
        exclude = {'check_time': {'longer': 4, 'shorter': 4},
                   'status': 'vi'}
        self.assertEqual(len(find_computing(filt, exclude)), 1)
        filt = {'disk_type': 's'}
        exclude = {'check_time': {'longer': 4, 'shorter': 4},
                   'status': 'fuck'}
        self.assertEqual(len(find_computing(filt, exclude)), 2)

    def test_find_key_error(self):
        filt = {'fuck': 'fuck'}
        self.assertRaises(KeyError, find_computing, filt, {})
        exclude = {'fuck': 'fuck'}
        self.assertRaises(KeyError, find_computing, {}, exclude)
        filt['check_time'] = {'ll': 'll'}
        self.assertRaises(KeyError, find_computing, filt, {})
        exclude['check_time'] = {'ll': 'll'}
        self.assertRaises(KeyError, find_computing, {}, exclude)

    def test_update_success(self):
        update_content = {
            'pc_type': 'v',
            'cpu': 'Xeon',
            'memory': 1023,
            'disk': 101,
            'disk_type': 'm',
            'os': 'mac os',
            'sn': 'c2',
            'expire_time': date(
                2015,
                12,
                3),
            'login': 'rongyuMo',
            'password': 'rongyuMo',
            'status': 'ri',
            'note': "hello world",
            'address': '127.0.0.9',
            'flag': False}
        comput1 = update_computing(1, update_content)
        comput2 = Computing.objects.get(id=1)
        self.assertEqual(comput1, comput2)
        self.assertEqual(comput1.pc_type, 'v')
        self.assertEqual(comput2.cpu, 'Xeon')
        self.assertEqual(comput1.memory, 1023)
        self.assertEqual(comput2.disk, 101)
        self.assertEqual(comput1.disk_type, 'm')
        self.assertEqual(comput1.os, 'mac os')
        # self.assertEqual(comput1.sn, 'c2')
        self.assertEqual(comput2.expire_time.year, 2015)
        self.assertEqual(comput1.expire_time.month, 12)
        self.assertEqual(comput2.expire_time.day, 3)
        self.assertEqual(comput1.login, 'rongyuMo')
        self.assertEqual(comput2.password, 'rongyuMo')
        self.assertEqual(comput1.status, 'ri')
        self.assertEqual(comput2.note, 'hello world')
        self.assertEqual(comput2.address, '127.0.0.9')
        self.assertEqual(comput1.flag, False)

    def test_update_invalid_ID(self):
        self.assertRaises(ComputingDoesNotExistError, update_computing, 10, {})

    def test_update_key_error(self):
        update_content = {'log': 'rongyu'}
        self.assertRaises(KeyError, update_computing, 1, update_content)

    def test_update_value_error(self):
        update_content = {'disk': 'abcd'}
        self.assertRaises(ValueError, update_computing, 1, update_content)

    def test_update_value_error2(self):
        update_content = {'memory': 'abcd'}
        self.assertRaises(ValueError, update_computing, 1, update_content)

    def test_update_ValidationError_error(self):
        update_content = {'expire_time': 'abcd'}
        self.assertRaises(ValidationError, update_computing, 1, update_content)

    def test_delete(self):
        self.assertEqual(delete_computing(1), True)
        self.assertEqual(len(Computing.objects.all()), 1)

    def test_delete_fail(self):
        self.assertRaises(ComputingDoesNotExistError, delete_computing, 10)

    def test_create_package(self):
        package = Package.objects.get(id=1)
        self.assertEqual(package.name, 'package1')
        self.assertEqual(package.cpu, 'core')
        self.assertEqual(package.memory, 1024)
        self.assertEqual(package.disk, 1024)
        self.assertEqual(package.disk_type, 's')
        self.assertEqual(package.os, 'windows')
        package = Package.objects.get(id=2)
        self.assertEqual(package.name, 'package2')
        self.assertEqual(package.cpu, 'xeon')
        self.assertEqual(package.memory, 1025)
        self.assertEqual(package.disk, 1025)
        self.assertEqual(package.disk_type, 'm')
        self.assertEqual(package.os, 'linux')

    def test_create_package_fail(self):
        package1 = {'cpu': 'core', 'pc_type': 'p',
                    # 'memory': 1024, 'disk': 1024, 'os': 'windows',
                    'disk_type': 's', 'name': 'package1'}
        self.assertRaises(Exception, create_package, package1)
    # create_package(package1)

    def test_package_update_success(self):
        update_content = {
            'name': 'pp1',
            'cpu': 'xeon',
            'pc_type': 'v',
            'memory': 2048,
            'disk': 2048,
            'disk_type': 'm',
            'os': 'mac os'}
        package1 = update_package(1, update_content)
        package2 = Package.objects.get(id=1)
        self.assertEqual(package1.name, 'pp1')
        self.assertEqual(package2.cpu, 'xeon')
        self.assertEqual(package1.pc_type, 'v')
        self.assertEqual(package2.memory, 2048)
        self.assertEqual(package1.disk, 2048)
        self.assertEqual(package2.disk_type, 'm')
        self.assertEqual(package1.os, 'mac os')

    def test_package_update_fail(self):
        update_content = {'n': 'n'}
        self.assertRaises(KeyError, update_package, 1, update_content)
        self.assertRaises(PackageDoesNotExistError, update_package, 10, {})

    def test_package_get_list(self):
        self.assertEqual(len(get_package_list()), 2)

    def test_package_delete_succ(self):
        self.assertEqual(delete_package(1), True)
        self.assertEqual(len(Package.objects.all()), 1)

    def test_package_delete_fail(self):
        self.assertRaises(PackageDoesNotExistError, delete_package, 5)
        self.assertRaises(PackageDoesNotExistError, delete_package, -1)

    #Test Goods View

    #Borrow
    def test_do_borrow_request(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))

        dic = {}
        dic['package'] = 'package1'
        dic['login'] = 'rongyu'
        dic['initial_password'] = 'rongyu'
        dic['reason'] = 'I want it'
        dic['flag'] = 'true'
        dic['data_content'] = 'rescue human'

        correct = self.manager.post(
            reverse('computing.views.do_borrow_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')

        dic['package'] = 'package2'
        correct = self.manager.post(
            reverse('computing.views.do_borrow_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')

        dic['name'] = 'answer42'
        correct = self.manager.post(
            reverse('computing.views.do_borrow_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')

        dic['package'] = 'none'
        dic['type'] = 'real'
        dic['cpu'] = 'core'
        dic['memory'] = 8
        dic['disk'] = 1024
        dic['disk_type'] = 'SSD'
        dic['os'] = 'windows'
        correct = self.manager.post(
            reverse('computing.views.do_borrow_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')

        dic['type'] = 'virtual'
        correct = self.manager.post(
            reverse('computing.views.do_borrow_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')

        dic['disk_type'] = 'HDD'
        correct = self.manager.post(
            reverse('computing.views.do_borrow_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')
    def test_do_return_request(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))

        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        computing3 = {'pc_type': 'p',
                      'cpu': 'core',
                      'memory': 1024,
                      'disk': 100,
                      'disk_type': 's',
                      'os': 'linux',
                      'expire_time': date.today() + timedelta(days=5),
                      'login': 'yurong',
                      'password': 'yurong',
                      'status': 'bo',
                      'account': Account.objects.get(id=1),
                      'note': message.tostring(),
                      'address': '127.0.0.2',
                      'flag': False,
                      'data_content': "",
                      'name': 'comp3',
                      'pack_name': 'pack2'}
        create_computing([computing3])

        dic = {}
        comp = Computing.objects.get(name='comp1')
        dic['id'] = comp.id
        correct = self.manager.post(
            reverse('computing.views.do_return_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'denied')
        comp = Computing.objects.get(name='comp3')
        dic['id'] = comp.id
        correct = self.manager.post(
            reverse('computing.views.do_return_request'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))
        delete_computing(comp.id)
    def test_do_approve_borrow(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))
        dic = {}
        comp = Computing.objects.get(name='comp1')
        message = Message()
        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        dic['id'] = comp.id
        dic['login'] = 'yefang0326'
        dic['initial_password'] = 'yefang0326'
        dic['note'] = message.tostring()
        dic['sn'] = comp.sn
        dic['ip'] = '127.0.0.1'
        correct = self.manager.post(
            reverse('computing.views.do_approve_borrow'),
            dic
        )
        self.assertRedirects(correct, reverse('computing.views.show_comp_verify'))

    def test_do_modif_request(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))
        message = Message()

        message.append({'direction': 'Recv', 'info_type': '',
                        'user_name': 'normal', 'text': 'hello world'})
        computing3 = {'pc_type': 'p',
                      'cpu': 'core',
                      'memory': 1024,
                      'disk': 100,
                      'disk_type': 's',
                      'os': 'linux',
                      'expire_time': date.today() + timedelta(days=5),
                      'login': 'yurong',
                      'password': 'yurong',
                      'status': 'bo',
                      'account': Account.objects.get(id=1),
                      'note': message.tostring(),
                      'address': '127.0.0.2',
                      'flag': False,
                      'data_content': "",
                      'name': 'comp3',
                      'pack_name': 'pack2'}
        create_computing([computing3])

        dic = {}
        comp = Computing.objects.get(name='comp1')
        dic['id'] = comp.id
        dic['reason'] = 'Shadow fiend comes, and I have to escape'
        correct = self.manager.post(
            reverse('computing.views.do_modif_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'denied')
        comp = Computing.objects.get(name='comp3')
        dic['id'] = comp.id
        correct = self.manager.post(
            reverse('computing.views.do_modif_request'),
            dic
        )
        self.assertEqual(correct.content.decode(), 'ok')
        delete_computing(comp.id)

    #Flag
    def test_do_set_flag(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))
        comp = Computing.objects.get(name='comp1')
        dic = {}
        dic['id'] = comp.id
        dic['flag'] = 'true'
        dic['content'] = 'very very important'
        correct = self.manager.post(
            reverse('computing.views.do_set_flag'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))
        dic['flag'] = 'false'
        correct = self.manager.post(
            reverse('computing.views.do_set_flag'),
            dic
        )
        self.assertRedirects(correct, reverse('goods.views.show_borrow'))

    #Package
    def test_do_package_create(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))
        pack1 = {
            'name':'pack_test',
            'cpu':'core',
            'memory':10,
            'disk':200,
            'os':'windows',
            'type':'real',
            'disktype':'SSD'
        }

        dic = {}
        dic['name'] = pack1['name']
        dic['cpu'] = pack1['cpu']
        dic['memory'] = pack1['memory']
        dic['disk'] = pack1['disk']
        dic['os'] = pack1['os']
        dic['type'] = pack1['type']
        dic['disktype'] = pack1['disktype']

        correct = self.manager.post(
            reverse('computing.views.do_create_package'),
            dic
        )
        self.assertRedirects(correct, reverse('computing.views.show_comp_manage'))

        dic['type'] = 'virtual'

        correct = self.manager.post(
            reverse('computing.views.do_create_package'),
            dic
        )
        self.assertRedirects(correct, reverse('computing.views.show_comp_manage'))

        # wrong_brw = self.manager.post(
        #     reverse('goods.views.do_reject_destroy'),
        #     dic
        # )
        # self.assertIsMessage(wrong_brw,
        #                      '')
    def test_do_package_get(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))
        dic = {}
        dic['name'] = 'package1'

        correct = self.manager.post(
            reverse('computing.views.do_get_package'),
            dic
        )
        p = Package.objects.get(name='package1')
        d = get_context_pack(p)
        self.assertEqual(correct.content.decode(),json.dumps(d))

    def test_do_package_delete(self):
        self.manager = Client()
        self.assertTrue(
            self.manager.login(
                username='rongyu',
                password='rongyu'))
        dic = {}
        dic['name'] = 'package2'

        correct = self.manager.post(
            reverse('computing.views.do_delete_package'),
            dic
        )
        self.assertRedirects(correct, reverse('computing.views.show_comp_manage'))
