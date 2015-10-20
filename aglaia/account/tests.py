from django.test import TestCase
from account.models import *
from account.interface import *
from django.contrib.auth.models import User
from django import forms

# from account.models import Department

class AccountTestCase(TestCase):

    def setUp(self):
        account1 = {'user_name': 'rongyu', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['a lab', 'b lab'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        account2 = {'user_name': 'yurong', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com', 'type': 'manager',
                    'real_name': 'yurong', 'department': ['a lab', 'b lab'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}

        d = [account1, account2]
        account = create_user(d)
        account[0].user.user_permissions.add(
            Permission.objects.get(codename="add_department"))
        account[0].user.user_permissions.add(
            Permission.objects.get(codename="add_account"))

    def test_create(self):
        self.assertEqual(len(Account.objects.all()), 2)
        account = Account.objects.get(id=1)
        self.assertEqual(account.user.username, 'rongyu')
        self.assertEqual(account.user.email, 'rongyu@rongy.com')
        self.assertEqual(account.real_name, 'rongyu')
        self.assertEqual(account.type, 'none')
        self.assertEqual(account.department.all()[0].depart_name, 'a lab')
        account = Account.objects.get(id=2)
        self.assertEqual(account.tel, '12345678')
        self.assertEqual(account.status, 'test')
        self.assertEqual(account.school_id, '0123456789')
        self.assertEqual(account.type, 'manager')
        self.assertEqual(account.department.all()[1].depart_name, 'b lab')

    def test_invalid_username_format(self):
        account3 = {'user_name': 'yufaf', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test'}
        self.assertRaises(FormatInvalidError, create_user, [account3])

    def test_invalid_password_format(self):
        account3 = {
            'user_name': 'yudfaf',
            'password': 'ronfasfasddfasdfasddfasfgyu',
            'email': 'rongyu@rongy.com',
            'real_name': 'rongyu',
            'department': ['xxx lab xxx'],
            'tel': '12345678',
            'status': 'test',
        }
        self.assertRaises(FormatInvalidError, create_user, [account3])

    def test_invalid_tel_format(self):
        account3 = {'user_name': 'yufaf', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345A678',
                    'status': 'test', }
        self.assertRaises(FormatInvalidError, create_user, [account3])

    def test_invalid_email_format(self):
        account3 = {'user_name': 'yufaf', 'password': 'rongyu',
                    'email': 'rongyurongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', }
        self.assertRaises(FormatInvalidError, create_user, [account3])

    def test_create_invalid_school_id_format(self):
        account3 = {'user_name': 'rongyu', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '01234'}
        self.assertRaises(FormatInvalidError, create_user, [account3])
        account3 = {
            'user_name': 'rongyu',
            'password': 'rongyu',
            'email': 'rongyu@rongy.com',
            'real_name': 'rongyu',
            'department': ['xxx lab xxx'],
            'tel': '12345678',
            'status': 'test',
            'school_id': '01234123131312312312312312'}
        self.assertRaises(FormatInvalidError, create_user, [account3])
        account3 = {'user_name': 'rongyu', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123q4'}
        self.assertRaises(FormatInvalidError, create_user, [account3])

    def test_invalid_type_format(self):
        account3 = {'user_name': 'yufaf', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com', 'type': '123',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', }
        self.assertRaises(FormatInvalidError, create_user, [account3])

    def test_key_error1(self):
        account3 = {'usefasdr_name': 'yufaf3', 'password': 'rongyu',
                    'email': 'rongyurongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        self.assertRaises(KeyError, create_user, [account3])
        account3 = {'user_name': 'yufaf3', 'password': 'rongyu',
                    'email': 'rongy@urongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'stafadftus': 'test', 'school_id': '0123456789'}
        self.assertRaises(KeyError, create_user, [account3])

    def test_key_error2(self):
        account3 = {'user_name': 'yufaf1', 'password': 'rongyu',
                    #'email': 'rongyurongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        self.assertRaises(KeyError, create_user, [account3])
        account3 = {'user_name': 'yufaf1', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    #'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        self.assertRaises(KeyError, create_user, [account3])

    def test_integrityError(self):
        account1 = {'user_name': 'rongyu', 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        self.assertRaises(IntegrityError, create_user, [account1])

    def test_type_error(self):
        account1 = {'user_name': 1234, 'password': 'rongyu',
                    'email': 'rongyu@rongy.com',
                    'real_name': 'rongyu', 'department': ['xxx lab xxx'],
                    'tel': '12345678',
                    'status': 'test', 'school_id': '0123456789'}
        self.assertRaises(TypeError, create_user, [account1])
    # 下面是find_users的测试函数

    def test_filter(self):
        exclude = {}
        filt = {'user_name': 'rongyu'}
        self.assertEqual(find_users(filt, exclude)[0].id, 1)
        filt = {'email': 'rongyu@rongy.com'}
        self.assertEqual(find_users(filt, exclude)[1].id, 2)
        filt = {'real_name': 'rongyu'}
        self.assertEqual(find_users(filt, exclude)[0].id, 1)
        filt = {'department': ['a lab', 'b lab']}
        self.assertEqual(find_users(filt, exclude)[1].id, 2)
        filt = {'tel': '12345678'}
        self.assertEqual(find_users(filt, exclude)[0].id, 1)
        filt = {'status': 'test'}
        self.assertEqual(find_users(filt, exclude)[1].id, 2)
        filt = {'school_id': '0123456789'}
        self.assertEqual(find_users(filt, exclude)[1].id, 2)
        filt = {'permission': ['add_department', 'add_account']}
        self.assertEqual(len(find_users(filt, exclude)), 1)
        filt = {'type': 'manager'}
        self.assertEqual(find_users(filt, exclude)[0].id, 2)
        filt = {'type': 'none'}
        self.assertEqual(find_users(filt, exclude)[0].id, 1)

    def test_exclude1(self):
        exclude = {'user_name': 'rongyu'}
        filt = {}
        self.assertEqual(find_users(filt, exclude)[0].id, 2)
        exclude = {'email': 'rongyu@rongy.com'}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'department': ['a lab']}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'department': ['b lab']}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'department': ['a lab', 'b lab']}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'department': ['c lab']}
        self.assertEqual(len(find_users(filt, exclude)), 2)
        exclude = {'tel': '12345678'}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'status': 'test'}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'school_id': '0123456789'}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'school_id': '12345678'}
        self.assertEqual(len(find_users(filt, exclude)), 2)
        exclude = {'permission': ['add_department']}
        self.assertEqual(len(find_users(filt, exclude)), 1)
        exclude = {'type': 'manager'}
        self.assertEqual(find_users(filt, exclude)[0].id, 1)
        exclude = {'type': 'none'}
        self.assertEqual(find_users(filt, exclude)[0].id, 2)

    def test_exclude_filter(self):
        filt = {'tel': '12345678', 'status': 'test', 'type': 'manager'}
        exclude = {
            'user_name': 'rongyu',
            'real_name': 'rongyu',
            'type': 'none'}
        self.assertEqual(find_users(filt, exclude)[0].id, 2)

    def test_useless_find(self):
        filt = {'user_name': 'fafasfa'}
        exclude = {}
        self.assertEqual(len(find_users(filt, exclude)), 0)
        exclude = {'user_name': 'fafasfa'}
        filt = {}
        self.assertEqual(len(find_users(filt, exclude)), 2)

    def test_invalid_key(self):
        filt = {'username': 'rongyu'}
        exclude = {}
        self.assertRaises(KeyError, find_users, filt, exclude)

    def test_update(self):
        update_content = {'real_name': 'yurong',
                          'email': '1582111936@qq.com',
                          'password': '123456',
                          'department': ['ACM', 'IEEE'],
                          'tel': '1234569',
                          'school_id': '11223344',
                          'status': 'test1',
                          'type': 'special'
                          }
        update_user(1, update_content)
        account1 = Account.objects.get(id=1)
        self.assertEqual(account1.real_name, 'yurong')
        self.assertEqual(account1.user.email, '1582111936@qq.com')
        self.assertEqual(account1.department.all()[0].depart_name, 'ACM')
        self.assertEqual(account1.department.all()[1].depart_name, 'IEEE')
        self.assertEqual(account1.tel, '1234569')
        self.assertEqual(account1.school_id, '11223344')
        self.assertEqual(account1.status, 'test1')
        self.assertEqual(account1.type, 'special')

    def test_update_invalid_id(self):
        self.assertRaises(UserDoesNotExistError, update_user, 10, {})

    def test_update_id_error(self):
        update_content = {'id': 1}
        self.assertRaises(IntegrityError, update_user, 1, update_content)
        update_content = {'user_name': 'fuck'}
        self.assertRaises(IntegrityError, update_user, 1, update_content)

    def test_update_invalid_key_error(self):
        update_content = {'user': 'haha'}
        self.assertRaises(KeyError, update_user, 1, update_content)
        update_content = {'permission': 'haha'}
        self.assertRaises(KeyError, update_user, 1, update_content)

    def test_update_type_error(self):
        update_content = {'real_name': 123}
        self.assertRaises(TypeError, update_user, 1, update_content)

    def test_format_error(self):
        update_content = {'tel': '1234q1'}
        self.assertRaises(FormatInvalidError, update_user, 1, update_content)
        update_content = {'password': '123'}
        self.assertRaises(FormatInvalidError, update_user, 1, update_content)
        update_content = {'password': 'fasfasfasdfasdfasdfasddfa'}
        self.assertRaises(FormatInvalidError, update_user, 1, update_content)
        update_content = {'email': 'rong@rong'}
        self.assertRaises(FormatInvalidError, update_user, 1, update_content)
        update_content = {'school_id': '12123@1'}
        self.assertRaises(FormatInvalidError, update_user, 1, update_content)
        update_content = {'type': '123'}
        self.assertRaises(FormatInvalidError, update_user, 1, update_content)

    def test_delete(self):
        self.assertEqual(delete_user(1), True)
        self.assertEqual(len(Account.objects.all()), 1)
        self.assertEqual(len(User.objects.all()), 1)

    def test_delete_fail(self):
        self.assertRaises(UserDoesNotExistError, delete_user, 10)
