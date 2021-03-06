import logging
import re
# DJANGO
from django.http import Http404
from datetime import datetime, timedelta
# PROJECT
from . import constants

logger = logging.getLogger('application')


def get_value_or_404(dict_, key):
    try:
        return dict_[key]
    except Exception as e:
        logger.error('Get value from dict error: ' + str(e))
        raise Http404(str(e))


def get_value_or_default(dict_, key, default=None):
    try:
        ret = dict_[key]
    except:
        ret = default
    return ret


def log(text, show=True):
    if show:
        print(text)


def log_error(text):
    logger.error(text)


def get_error_text(code):
    if code:
        return constants.ERROR_CONFIG[code][0]


def raise_error(code=None, text=None):
    if code:
        error_text = constants.ERROR_CONFIG[code][0]
        logger.error(error_text)
        raise ValueError(error_text)
    elif text:
        logger.error(text)
        raise ValueError(text)
    else:
        raise ValueError('A server error occurred')


def create_response_obj(status, message=None, code=None, data=None):
    if status == 'success':
        val = 1
        success = True
        code = '201'
    elif status == 'error':
        val = 0
        success = False
    resp = {'value': val, 'success': success, 'status': status, 'message': message, 'code': code, 'data': data}
    return resp


def success_resp(data, message=None):
    return create_response_obj(status='success', message=message, data=data)


def error_resp(message, data=None):
    return create_response_obj(status='error', message=message, data=data)


def create_error_object(message, code=None):
    errors = []
    error = {'status': None, 'code': code, 'message': None, 'extra_data': None}
    error['message'] = message
    errors.append(error)
    return errors


def python_btoa(string):
    import base64
    string_byte = string.encode("utf-8")
    encoded_byte = base64.b64encode(string_byte)
    encoded_string = encoded_byte.decode("utf-8")
    return encoded_string

def random_with_N_digits(n):
    from random import randint
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

########################### BOOLEAN #################################

def to_bool(val):
    if val is None:
        return None
    elif val is True or val is False:
        return val
    elif val.lower() == 'true':
        return True
    elif val.lower() == 'false':
        return False
    else:
        return None

def convertBoolean(bool_str):
    if bool_str.lower() == 'false':
        return False
    elif bool_str.lower() == 'true':
        return True
    else:
        return None

########################### Email, Phone #################################
def check_for_valid_email(email):
    if not email:
        return False
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
        return True
    else:
        return False

def validate_email(email):
    if email is None:
        return False
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True


def validate_phone(phone):
    if phone is None:
        return False
    if phone[:1] == '+' and phone[1:].isdigit():
        return True
    elif phone.isdigit():
        return True
    return False


def validate_get_phone(phone):
    phone_number = None
    phone_code = None
    if not validate_phone(phone):
        raise_error('ERR-GNRL-INVALID-PHONE')
    elif len(phone) < 10:
        raise_error('ERR-GNRL-INVALID-PHONE')
    elif phone[0] != '+' and len(phone) == 10:
        phone_number = phone
        phone_code = '91'
    elif phone[0] == '0' and len(phone) == 11:
        phone_number = phone[1:]
        phone_code = '91'
    elif phone[:2] == '91' and len(phone) == 12:
        phone_number = phone[2:]
        phone_code = phone[:2]
    elif phone[:3] == '+91' and len(phone) == 13:
        phone_number = phone[3:]
        phone_code = phone[1:3]
    elif not phone_number or not phone_code:
        raise_error('ERR-GNRL-INVALID-PHONE')

    data = {'phone_number': phone_number, 'phone_code': phone_code}
    return data


def get_phone_or_null(phone):
    phone_number = None
    phone_code = None
    if not validate_phone(phone):
        return None
    elif len(phone) < 10:
        return None
    elif phone[0] != '+' and len(phone) == 10:
        phone_number = phone
        phone_code = '91'
    elif phone[0] == '0' and len(phone) == 11:
        phone_number = phone[1:]
        phone_code = '91'
    elif phone[:2] == '91' and len(phone) == 12:
        phone_number = phone[2:]
        phone_code = phone[:2]
    elif phone[:3] == '+91' and len(phone) == 13:
        phone_number = phone[3:]
        phone_code = phone[1:3]
    elif not phone_number or not phone_code:
        return None

    data = {'phone_number': phone_number, 'phone_code': phone_code}
    return data