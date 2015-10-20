from log.models import *
from datetime import *


def create_log(type, *args, **kwargs):
    create_log_func[type](*args, **kwargs)


def create_account_log(user_id, target, action, description):
    try:
        logAccount = LogAccount(user_id=user_id,
                                target=target, action=action,
                                time=datetime.now(),
                                description=description)
        logAccount.save()
    except Exception as e:
        raise e


def create_computing_log(user_id, target, action, description):
    try:
        logComputing = LogComputing(user_id=user_id,
                                    target=target, action=action,
                                    time=datetime.now(),
                                    description=description)
        logComputing.save()
    except Exception as e:
        raise e


def create_borrow_log(user_id, target, action, description):
    try:
        logBorrow = LogBorrow(user_id=user_id,
                              target=target, action=action,
                              time=datetime.now(),
                              description=description)
        logBorrow.save()
    except Exception as e:
        raise e


def create_single_log(user_id, target, action, description):
    try:
        logSingle = LogSingle(user_id=user_id,
                              target=target, action=action,
                              time=datetime.now(),
                              description=description)
        logSingle.save()
    except Exception as e:
        raise e

create_log_func = {
    'single': create_single_log,
    'computing': create_computing_log,
    'user': create_account_log,
    'borrow': create_borrow_log
}
