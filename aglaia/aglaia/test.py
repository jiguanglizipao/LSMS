from django.test import TestCase
from aglaia.message_center import Message


class MessageCenterTestCase(TestCase):

    def setUp(self):
        self.message = Message(max_num=5)

    def test___init__(self):
        self.assertEqual(self.message.root.get('max_num'), '5')
        self.assertEqual(len(self.message.root), 0)

    def test_append(self):
        self.message.append(
            {'direction': 'Recv', 'info_type': 'test', 'info_data': 'TEST',
             'user_name': '1', 'text': 'text1'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'aaa', 'info_data': '111',
             'user_name': '2', 'text': 'text2'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '3', 'text': 'text3'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '4', 'text': 'text4'})
        self.message.append(
            {'direction': 'Send', 'info_type': '', 'user_name': '5',
             'text': 'text5'})
        self.assertEqual(len(self.message.root), 5)
        self.assertEqual(self.message.root[0].tag, 'message')
        self.assertEqual(self.message.root[0].get('direction'), 'Recv')
        self.assertEqual(self.message.root[0].get('info_type'), 'test')
        self.assertEqual(self.message.root[0].find('user_name').text, '1')
        self.assertEqual(self.message.root[0].find('text').text, 'text1')
        self.assertEqual(self.message.root[0].find('info_data').text, 'TEST')

    def test_append_KeyError(self):
        arg = {
            'direction': '123',
            'info_type': 'test',
            'info_data': 'TEST',
            'user_name': '1',
            'text': 'text1'}
        self.assertRaises(KeyError, self.message.append, arg)

    def test_append_Exception(self):
        arg = {
            'direction1': 'Recv',
            'info_type': 'test',
            'info_data': 'TEST',
            'user_name': '1',
            'text': 'text1'}
        self.assertRaises(Exception, self.message.append, arg)
        arg = {
            'direction': 'Recv',
            'info_type1': 'test',
            'info_data': 'TEST',
            'user_name': '1',
            'text': 'text1'}
        self.assertRaises(Exception, self.message.append, arg)
        arg = {
            'direction': 'Recv',
            'info_type': 'test',
            'info_data1': 'TEST',
            'user_name': '1',
            'text': 'text1'}
        self.assertRaises(Exception, self.message.append, arg)
        arg = {
            'direction': 'Recv',
            'info_type': 'test',
            'info_data': 'TEST',
            'user_name1': '1',
            'text': 'text1'}
        self.assertRaises(Exception, self.message.append, arg)
        arg = {
            'direction': 'Recv',
            'info_type': 'test',
            'info_data': 'TEST',
            'user_name': '1',
            'text1': 'text1'}
        self.assertRaises(Exception, self.message.append, arg)
        arg = {
            'direction': 'Recv',
            'info_type': 'test',
            'user_name': '1',
            'text': 'text1'}
        self.assertRaises(Exception, self.message.append, arg)

    def test_append_max_num(self):
        self.message.append(
            {'direction': 'Recv', 'info_type': 'test', 'info_data': 'TEST',
             'user_name': '1', 'text': 'text1'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'aaa', 'info_data': '111',
             'user_name': '2', 'text': 'text2'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '3', 'text': 'text3'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '4', 'text': 'text4'})
        self.message.append(
            {'direction': 'Send', 'info_type': '', 'user_name': '5',
             'text': 'text5'})
        self.message.append(
            {'direction': 'Send', 'info_type': '', 'user_name': '6',
             'text': 'text6'})
        self.assertEqual(len(self.message.root), 5)
        self.assertEqual(self.message.root[0].tag, 'message')
        self.assertEqual(self.message.root[0].get('direction'), 'Send')
        self.assertEqual(self.message.root[0].get('info_type'), 'aaa')
        self.assertEqual(self.message.root[0].find('user_name').text, '2')
        self.assertEqual(self.message.root[0].find('text').text, 'text2')
        self.assertEqual(self.message.root[0].find('info_data').text, '111')

    def test_index(self):
        self.message.append(
            {'direction': 'Recv', 'info_type': 'test', 'info_data': 'TEST',
             'user_name': '1', 'text': 'text1'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'aaa', 'info_data': '111',
             'user_name': '2', 'text': 'text2'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '3', 'text': 'text3'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '4', 'text': 'text4'})
        self.message.append(
            {'direction': 'Send', 'info_type': '', 'user_name': '5',
             'text': 'text5'})
        self.assertEqual(self.message.index(3)['direction'], 'Send')
        self.assertEqual(self.message.index(3)['info_type'], 'bbb')
        self.assertEqual(self.message.index(3)['info_data'], '222')
        self.assertEqual(self.message.index(3)['user_name'], '4')
        self.assertEqual(self.message.index(3)['text'], 'text4')

    def test_last(self):
        self.message.append(
            {'direction': 'Recv', 'info_type': 'test', 'info_data': 'TEST',
             'user_name': '1', 'text': 'text1'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'aaa', 'info_data': '111',
             'user_name': '2', 'text': 'text2'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '3', 'text': 'text3'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '4', 'text': 'text4'})
        self.assertEqual(self.message.index(3)['direction'], 'Send')
        self.assertEqual(self.message.index(3)['info_type'], 'bbb')
        self.assertEqual(self.message.index(3)['info_data'], '222')
        self.assertEqual(self.message.index(3)['user_name'], '4')
        self.assertEqual(self.message.index(3)['text'], 'text4')

    def test_tostring_origin(self):
        self.message.append(
            {'direction': 'Recv', 'info_type': 'test', 'info_data': 'TEST',
             'user_name': '1', 'text': 'text1'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'aaa', 'info_data': '111',
             'user_name': '2', 'text': 'text2'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '3', 'text': 'text3'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '4', 'text': 'text4'})
        self.message.append(
            {'direction': 'Send', 'info_type': '', 'user_name': '5',
             'text': 'text5'})
        tmp = Message(origin=self.message.tostring().decode())
        self.assertEqual(self.message.tostring(), tmp.tostring())
        self.assertRaises(Exception, self.message.__init__(), 'test')

    def test_pretty_print(self):
        self.message.append(
            {'direction': 'Recv', 'info_type': 'test', 'info_data': 'TEST',
             'user_name': '1', 'text': 'text1'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'aaa', 'info_data': '111',
             'user_name': '2', 'text': 'text2'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '3', 'text': 'text3'})
        self.message.append(
            {'direction': 'Send', 'info_type': 'bbb', 'info_data': '222',
             'user_name': '4', 'text': 'text4'})
        self.message.append(
            {'direction': 'Send', 'info_type': '', 'user_name': '5',
             'text': 'text5'})
        tmp = Message(origin=self.message.pretty_print().decode())
        self.assertEqual(tmp.index(3)['direction'], 'Send')
        self.assertEqual(tmp.index(3)['info_type'], 'bbb')
        self.assertEqual(tmp.index(3)['info_data'], '222')
        self.assertEqual(tmp.index(3)['user_name'], '4')
        self.assertEqual(tmp.index(3)['text'], 'text4')
