from datetime import *
from django.core.exceptions import *
from django.db.utils import *
from django.db.models import *
from account.models import *
from account.interface import *
from computing.models import *
from log.interface import *
from aglaia.messages import *
from random import Random


UNKNOWN_ADDR = '0.0.0.0'
UNKNOWN_PASS = ''


class ComputingDoesNotExistError(Exception):
    pass


class ServerDoesNotExistError(Exception):
    pass


class PackageDoesNotExistError(Exception):
    pass


def random_str(randomlength=16):
    ran = str()
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        ran += chars[random.randint(0, length)]
    return ran


def create_computing(computing_list):
    new_computing = []
    for computing in computing_list:
        try:
            name = computing['name']
            pack_name = computing['pack_name']
            pc_type = computing['pc_type']
            cpu = computing['cpu']
            memory = computing['memory']
            disk = computing['disk']
            disk_type = computing['disk_type']
            os = computing['os']
            sn = random_str()
            expire_time = computing['expire_time']
            login = computing['login']
            password = computing['password']
            status = computing['status']
            account = computing['account']
            note = computing['note']
            address = computing['address']
            if computing['flag'] == 'True' or computing[
                    'flag'] == 'true' or computing['flag'] == 'TRUE':
                flag = True
            else:
                flag = False
            data_content = computing['data_content']
            if (len(note) > 500):
                raise FormatInvalidError("Note is too long")
            try:
                comput = Computing(pc_type=pc_type, cpu=cpu,
                                   memory=memory, disk=disk,
                                   disk_type=disk_type, os=os,
                                   sn=sn,
                                   expire_time=expire_time,
                                   login=login, password=password,
                                   status=status, account=account, note=note,
                                   address=address, flag=flag,
                                   name=name, pack_name=pack_name,
                                   data_content=data_content)
                comput.save()
                new_computing.append(comput)
            except TypeError:
                raise TypeError("Value type is wrong")
            except ValueError:
                raise ValueError("Account's type should be Account")
        except KeyError:
            raise KeyError("Key's content is missing or wrong")
    return new_computing


def find_computing(filt, exclude):
    correct_keys = [
        'pc_type',
        'disk_type',
        'check_time',
        'os',
        'sn',
        'status',
        'account',
        'address',
        'flag',
        'pack_name',
        'data_content']
    for key in filt.keys():
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)
    for key in exclude.keys():
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)
    q = Computing.objects.all()
    try:
        # filter
        if 'pack_name' in filt:
            q = q.filter(pack_name=filt['pack_name'])
        if 'pc_type' in filt:
            q = q.filter(pc_type=filt['pc_type'])
        if 'disk_type' in filt:
            q = q.filter(disk_type=filt['disk_type'])
        if 'os' in filt:
            q = q.filter(os=filt['os'])
        if 'sn' in filt:
            q = q.filter(sn=filt['sn'])
        if 'status' in filt:
            q = q.filter(status=filt['status'])
        if 'account' in filt:
            q = q.filter(account=filt['account'])
        if 'address' in filt:
            q = q.filter(address=filt['address'])
        if 'flag' in filt:
            q = q.filter(flag=filt['flag'])
        if 'check_time' in filt:
            time_dict = filt['check_time']
            if (not 'longer' in time_dict) and (not 'shorter' in time_dict):
                raise KeyError("The content of check_time is wrong")
            if 'longer' in time_dict:
                q = q.filter(
                    expire_time__gt=date.today() +
                    timedelta(
                        days=time_dict['longer']))
            if 'shorter' in time_dict:
                q = q.filter(
                    expire_time__lte=date.today() +
                    timedelta(
                        days=time_dict['shorter']))
        if 'data_content' in filt:
            q = q.filter(data_content=filt['data_content'])
        # exclude
        if 'pc_type' in exclude:
            q = q.exclude(pc_type=exclude['pc_type'])
        if 'disk_type' in exclude:
            q = q.exclude(disk_type=exclude['disk_type'])
        if 'os' in exclude:
            q = q.exclude(os=exclude['os'])
        if 'sn' in exclude:
            q = q.exclude(sn=exclude['sn'])
        if 'status' in exclude:
            q = q.exclude(status=exclude['status'])
        if 'account' in exclude:
            q = q.exclude(account=exclude['account'])
        if 'address' in exclude:
            q = q.exclude(address=exclude['address'])
        if 'flag' in exclude:
            q = q.exclude(flag=exclude['flag'])
        if 'check_time' in exclude:
            time_dict = exclude['check_time']
            if (not ('longer' in time_dict)) and (
                    not ('shorter' in time_dict)):
                raise KeyError("The content of check_time is wrong")
            if ('longer' in time_dict) and ('shorter' in time_dict):
                q = q.exclude(
                    Q(
                        expire_time__gt=date.today() +
                        timedelta(
                            days=time_dict['longer'])) & Q(
                        expire_time__lte=date.today() +
                        timedelta(
                            days=time_dict['shorter'])))
            if ('longer' in time_dict) and (not ('shorter' in time_dict)):
                q = q.exclude(
                    expire_time__gt=date.today() +
                    timedelta(
                        days=time_dict['longer']))
            if (not ('longer' in time_dict)) and ('shorter' in time_dict):
                q = q.exclude(
                    expire_time__lte=date.today() +
                    timedelta(
                        days=time_dict['shorter']))
        if 'data_content' in exclude:
            q = q.exclude(data_content=exclude['data_content'])
        return q
    except Exception:
        raise


def update_computing(computing_id, update_content):
    correct_keys = ['pc_type', 'cpu', 'memory', 'disk', 'os', 'sn',
                    'disk_type', 'expire_time', 'login',
                    'password', 'status', 'note', 'address', 'flag',
                    'name', 'data_content']
    for key in update_content:
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)
    computing = None
    try:
        computing = Computing.objects.get(id=computing_id)
    except:
        raise ComputingDoesNotExistError("Invalid ID")
    try:
        if 'name' in update_content:
            computing.name = update_content['name']
        if 'pc_type' in update_content:
            computing.pc_type = update_content['pc_type']
        if 'cpu' in update_content:
            computing.cpu = update_content['cpu']
        if 'memory' in update_content:
            computing.memory = update_content['memory']
        if 'disk' in update_content:
            computing.disk = update_content['disk']
        if 'disk_type' in update_content:
            computing.disk_type = update_content['disk_type']
        if 'os' in update_content:
            computing.os = update_content['os']
        if 'expire_time' in update_content:
            computing.expire_time = update_content['expire_time']
        if 'login' in update_content:
            computing.login = update_content['login']
        if 'password' in update_content:
            computing.password = update_content['password']
        if 'status' in update_content:
            computing.status = update_content['status']
        if 'note' in update_content:
            note = update_content['note']
            # if (len(note) > 500):
            #     raise FormatInvalidError("Format of note is invalid")
            computing.note = note
        if 'address' in update_content:
            computing.address = update_content['address']
        if 'flag' in update_content:
            computing.flag = update_content['flag']
        if 'data_content' in update_content:
            computing.data_content = update_content['data_content']
        if 'sn' in update_content and update_content['sn'] != '':
            computing.sn = update_content['sn']

        computing.save()
        return computing
    except KeyError:
        raise KeyError("key content missing or wrong")
    except TypeError:
        raise TypeError("value type wrong")
    except ValueError:
        raise ValueError("value wrong")


def delete_computing(computing_id):
    comput = None
    try:
        comput = Computing.objects.get(id=computing_id)
    except:
        raise ComputingDoesNotExistError("computing does not exist")
    comput.delete()
    return True


# following are interfaces for Server:
def create_server(server_list):
    new_servers = []
    for server in server_list:
        try:
            new_server = Server(status=server['status'],
                                description=server['description'],
                                name=server['name'],
                                configuration=server['configuration'])
            new_server.save()
            new_servers.append(new_server)
        except TypeError:
            raise TypeError("Value type is wrong")
        except ValueError:
            raise ValueError("Account's type should be Account")
        except KeyError:
            raise KeyError("Key's content is missing or wrong")
    return new_servers


def find_server(filt, exclude):
    correct_keys = ['status', 'description',
                    'name', 'configuration']
    for key in filt.keys():
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)
    for key in exclude.keys():
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)

    q = Server.objects.all()
    try:
        if 'status' in filt:
            q = q.filter(status=filt['status'])
        if 'description' in filt:
            q = q.filter(description=filt['description'])
        if 'name' in filt:
            q = q.filter(name=filt['name'])
        if 'configuration' in filt:
            q = q.filter(configuration=filt['configuration'])
        if 'status' in exclude:
            q = q.exclude(status=exclude['status'])
        if 'description' in exclude:
            q = q.exclude(description=exclude['description'])
        if 'name' in exclude:
            q = q.exclude(name=exclude['name'])
        if 'configuration' in exclude:
            q = q.exclude(configuration=exclude['configuration'])
        return q
    except Exception:
        raise


def update_server(server_id, update_content):
    correct_keys = ['status', 'description',
                    'configuration', 'name']
    for key in update_content:
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)
    server = None
    try:
        server = Server.objects.get(id=server_id)
    except:
        raise ServerDoesNotExistError("Invalid ID")
    try:
        if 'status' in update_content:
            server.status = update_content['status']
        if 'description' in update_content:
            server.description = update_content['description']
        if 'configuration' in update_content:
            server.configuration = update_content['configuration']
        if 'name' in update_content:
            server.name = update_content['name']
        server.save()
        return server
    except KeyError:
        raise KeyError("key content missing or wrong")
    except TypeError:
        raise TypeError("value type wrong")
    except ValueError:
        raise ValueError("value wrong")


def delete_server(server_id):
    server = None
    try:
        server = Server.objects.get(id=server_id)
    except:
        raise ServerDoesNotExistError("Server does not exist")
    server.delete()
    return True


def create_package(create_content):
    try:
        package = Package(cpu=create_content['cpu'],
                          pc_type=create_content['pc_type'],
                          memory=create_content['memory'],
                          disk=create_content['disk'],
                          disk_type=create_content['disk_type'],
                          name=create_content['name'],
                          os=create_content['os'])
        package.save()
        return package
    except Exception as e:
        raise Exception("Error in create package:" + e.__str__())


def update_package(package_id, update_content):
    package = None
    correct_keys = ['name', 'cpu', 'os',
                    'pc_type', 'memory',
                    'disk', 'disk_type']
    for key in update_content:
        if not (key in correct_keys):
            raise KeyError("The key: %s is wrong", key)
    try:
        package = Package.objects.get(id=package_id)
    except:
        raise PackageDoesNotExistError("Package does not exist")
    try:
        if 'name' in update_content:
            package.name = update_content['name']
        if 'cpu' in update_content:
            package.cpu = update_content['cpu']
        if 'pc_type' in update_content:
            package.pc_type = update_content['pc_type']
        if 'memory' in update_content:
            package.memory = update_content['memory']
        if 'disk' in update_content:
            package.disk = update_content['disk']
        if 'disk_type' in update_content:
            package.disk_type = update_content['disk_type']
        if 'os' in update_content:
            package.os = update_content['os']
        package.save()
        return package
    except:
        raise Exception("Error in update package")


def get_package_list():
    return Package.objects.all()


def delete_package(package_id):
    package = None
    try:
        package = Package.objects.get(id=package_id)
    except:
        raise PackageDoesNotExistError("package does not exist")
    package.delete()
    return True


def packed_create_computing(request, *args, **kwargs):
    desc = ''
    if 'log' in kwargs:
        desc = kwargs.pop('log')
    ret = create_computing(*args, **kwargs)
    for c in ret:
        create_log('computing', user_id=request.user.id,
                   target=c, action='create computing',
                   description=desc)
    return ret


def packed_find_computing(request, *args, **kwargs):
    return find_computing(*args, **kwargs)


def packed_update_computing(request, *args, **kwargs):
    desc = ''
    if 'log' in kwargs:
        desc = kwargs.pop('log')
    elif len(args) < 1:
        desc = kwargs['update_content']
    else:
        desc = args[1]
        flag = desc['flag']
        data_content = ''
        if flag:
            data_content = desc['data_content']
        desc = get_flag_log(flag, data_content)
    ret = update_computing(*args, **kwargs)
    create_log('computing', user_id=request.user.id,
               target=ret, action='update computing',
               description=desc)
    return ret


def packed_delete_computing(request, *args, **kwargs):
    return delete_computing(*args, **kwargs)


def packed_create_server(request, *args, **kwargs):
    return create_server(*args, **kwargs)


def packed_find_server(request, *args, **kwargs):
    return find_server(*args, **kwargs)


def packed_update_server(request, *args, **kwargs):
    return update_server(*args, **kwargs)


def packed_delete_server(request, *args, **kwargs):
    return delete_server(*args, **kwargs)


def packed_create_package(request, *args, **kwargs):
    return create_package(*args, **kwargs)


def packed_update_package(request, *args, **kwargs):
    return update_package(*args, **kwargs)


def packed_delete_package(request, *args, **kwargs):
    return delete_package(*args, **kwargs)
