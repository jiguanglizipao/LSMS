from lxml import etree
import time


class Message:

    def __init__(self, origin='', max_num=400):
        if origin:
            try:
                self.root = etree.fromstring(origin.encode())
            except Exception as e:
                raise e
        else:
            self.root = etree.Element("root")
            self.root.set('max_num', str(max_num))
            self.setTime()

    def append(self, data):
        try:
            message = etree.SubElement(self.root, "message")

            if not (data['direction'] == 'Recv' or data[
                    'direction'] == 'Send'):
                raise KeyError('direction must be Recv or Send')
            message.set('direction', data['direction'])
            message.set('info_type', data['info_type'])
            sub_user = etree.SubElement(message, 'user_name')
            sub_user.text = data['user_name']
            sub_time = etree.SubElement(message, 'time')
            sub_time.text = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(
                    time.time()))
            sub_text = etree.SubElement(message, 'text')
            sub_text.text = data['text']
            if data['info_type']:
                sub_info = etree.SubElement(message, 'info_data')
                sub_info.text = data['info_data']

            while len(self.root) > int(self.root.get('max_num')):
                self.root.remove(self.root[0])

        except Exception as e:
            raise e

        return etree.tostring(
            self.root,
            encoding="utf-8",
            xml_declaration=True)

    def __sizeof__(self):
        return len(self.root)

    def index(self, i):
        try:
            message = self.root[i]
            data = dict()
            data['direction'] = message.get('direction')
            data['info_type'] = message.get('info_type')
            for child in message:
                data[child.tag] = child.text
            return data

        except Exception as e:
            raise e

    def pretty_print(self):
        return etree.tostring(
            self.root,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True)

    def tostring(self):
        return etree.tostring(
            self.root,
            encoding="utf-8",
            xml_declaration=True)

    def setTime(self):
        self.root.set('time', time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(
                    time.time())))

    def getTime(self):
        return self.root.get('time')

    def last(self):
        return self.index(self.__sizeof__() - 1)


# if __name__ == "__main__":
#     message = Message('', 5)
#     message.append({'direction': 'Recv', 'info_type': '', 'user_name': '1', 'text': 'text1'})
#     message.append({'direction': 'Send', 'info_type': 'aaa', 'info_data': '111', 'user_name': '2', 'text': 'text2'})
#     message.append({'direction': 'Send', 'info_type': 'bbb', 'info_data': '222', 'user_name': '3', 'text': 'text3'})
#     message.append({'direction': 'Send', 'info_type': 'bbb', 'info_data': '222', 'user_name': '4', 'text': 'text4'})
#     message.append({'direction': 'Send', 'info_type': '', 'user_name': '5', 'text': 'text5'})
#     message.append({'direction': 'Send', 'info_type': '', 'user_name': '6', 'text': 'text6'})
#     print(message.pretty_print().decode())
#     print(message.index(1))
#     print(message.__sizeof__())
#     print(message.last())
#     print(message.last()['text'])
