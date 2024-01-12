import logging
import copy
import json
import inspect
from logging import Formatter, PercentStyle
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.urls import resolve
from django.core.serializers.json import DjangoJSONEncoder
from business.common.designpatterns import SingletonClass
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.response import Response

class CustomFormatter(Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        self._style = CustomStyle(fmt)
        if validate:
            self._style.validate()

        self._fmt = self._style._fmt
        self.datefmt = datefmt


class CustomStyle(PercentStyle):
    def _format(self, record):
        if "user_key" not in record.__dict__:
            record.__dict__["user_key"] = "library"
        if "channel" not in record.__dict__:
            record.__dict__["channel"] = "NONE"
        if "direction" not in record.__dict__:
            record.__dict__["direction"] = "NONE"
        return self._fmt % record.__dict__


def task_info(logger, msg, extra):
    logger.info(msg=msg, extra=extra)


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _get_client_useragent(request):
    http_user_agent = request.META.get('HTTP_USER_AGENT', '')
    return http_user_agent


def client_info_logging(logger, check_large_list=False, check_private_info=False):
    def inner(func):
        if not logger.isEnabledFor(logging.INFO):
            return func

        def wrapper(*args, **kwargs):
            function_name = args[0].action

            if logger.isEnabledFor(logging.INFO):
                request_log_data = _modify_for_logging(data=args[1].data, check_private_info=check_private_info)
                logger.info(msg=f"[CLIENT_INFO] {function_name}, REQUEST : {request_log_data}, "
                                f"{_get_client_ip(args[1])} {_get_client_useragent(args[1])}",                                
                            extra={'channel': 'NONE', 'user_key': 'NONE', 'direction': 'NONE',
                                   'message_type': 'text', 'status': 'VA'})
            response = func(*args, **kwargs)
            if logger.isEnabledFor(logging.INFO):
                response_log_data = _modify_for_logging(data=response.data, check_large_list=check_large_list)
                logger.info(msg=f"[CLIENT_INFO] {function_name}, RESPONSE {response_log_data}, REQUEST : {request_log_data}, "
                                f"{_get_client_ip(args[1])} {_get_client_useragent(args[1])}",
                            extra={'channel': 'NONE', 'user_key': 'NONE', 'direction': 'NONE',
                                   'message_type': 'text', 'status': 'VA'})
            return response
        return wrapper
    return inner


def fount_request_response(logger, check_large_list=False, check_private_info=False):
    def inner(func):
        if not logger.isEnabledFor(logging.INFO):
            return func

        def wrapper(*args, **kwargs):
            if logger.isEnabledFor(logging.INFO):
                request_log_data = _modify_for_logging(data=kwargs, check_private_info=check_private_info)
                logger.info(msg=f"{func.__name__}, REQUEST : {request_log_data}, ",
                            extra={'channel': "NONE", 'user_key': 'NONE', 'direction': '[WEB -> BUSINESS]',
                                   'message_type': 'text', 'status': 'VA'})
            response = func(*args, **kwargs)

            try:
                if type(response) != dict:
                    response = dict(response)
            except ValueError:
                return response

            if logger.isEnabledFor(logging.INFO):
                response_log_data = _modify_for_logging(data=response, check_large_list=check_large_list)
                logger.info(msg=f"{func.__name__}, REQUEST : {request_log_data}, RESPONSE : {response_log_data}",
                            extra={'channel': "NONE", 'user_key': 'NONE', 'direction': '[BUSINESS -> WEB]',
                                   'message_type': 'text', 'status': 'VA'})
            return response
        return wrapper
    return inner    


def fep_request_response(logger, check_large_list=False, check_private_info=False):
    def inner(func):
        if not logger.isEnabledFor(logging.INFO):
            return func

        def wrapper(*args, **kwargs):
            if logger.isEnabledFor(logging.INFO):
                request_log_data = _modify_for_logging(data=kwargs, check_private_info=check_private_info)
                logger.info(msg=f"{func.__name__}, REQUEST : {request_log_data}",
                            extra={'channel': 'NONE', 'user_key': 'NONE', 'direction': '[BUSINESS -> FEP]',
                                   'message_type': 'text', 'status': 'VA'})
            response = func(*args, **kwargs)
            if logger.isEnabledFor(logging.INFO):
                response_log_data = _modify_for_logging(data=response, check_large_list=check_large_list)
                logger.info(msg=f'{func.__name__}, REQUEST : {request_log_data}, RESPONSE : {response_log_data}',
                            extra={'channel': 'NONE', 'user_key': 'NONE', 'direction': '[FEP -> BUSINESS]',
                                   'message_type': 'text', 'status': 'VA'})
            return response
        return wrapper
    return inner


def kdb_request_response(logger, check_large_list=False, check_private_info=False):
    def inner(func):
        if not logger.isEnabledFor(logging.INFO):
            return func

        def wrapper(*args, **kwargs):
            function_name = inspect.stack()[2][3]
            if logger.isEnabledFor(logging.INFO):
                request_log_data = _modify_for_logging(data=kwargs['body'], check_private_info=check_private_info)                

                logger.info(msg=f"{function_name}, REQUEST : {request_log_data}",
                            extra={'channel': 'NONE', 'user_key': 'NONE', 'direction': '[FEP -> KDB]',
                                   'message_type': 'text', 'status': 'VA'})
            response = func(*args, **kwargs)
            if logger.isEnabledFor(logging.INFO):
                response_log_data = _modify_for_logging(data=response, check_large_list=check_large_list)
                logger.info(msg=f'{function_name}, REQUEST : {request_log_data}, RESPONSE : {response_log_data}',
                            extra={'channel': 'NONE', 'user_key': 'NONE', 'direction': '[KDB -> FEP]',
                                   'message_type': 'text', 'status': 'VA'})
            return response
        return wrapper
    return inner


def _modify_for_logging(data, check_large_list=False, check_private_info=False):
    if not isinstance(data, dict):
        return data

    log_data = copy.deepcopy(data)
    if check_large_list:
        log_data = _exclude_large_list(log_data)
    if check_private_info:
        log_data = _remove_private_info(log_data)
    log_data = _json_dumps_msg(log_data)

    return log_data


def _exclude_large_list(data):
    max_size = 100
    for key in list(data.keys()):
        if type(data[key]) == list and len(data[key]) > max_size:
            data[key] = 'length: ' + str(len(data[key]))

    return data


def _remove_private_info(data):
    private_info_keys = ['name', 'birth_date', 'phone_no']
    for key in private_info_keys:
        if data.get(key) is not None:
            data[key] = ''

    return data


def _json_dumps_msg(data):
    return json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False)


class FountCustomLoggerClass(SingletonClass):
    __excutor = ThreadPoolExecutor(20)

    def set_logger(self, logger_name):
        pass

    def info(self, logger_name="", msg="", extra={}):
        logger = logging.getLogger(logger_name)
        if logger.isEnabledFor(logging.INFO):
            if settings["LOG_THREAD"]:
                self.__excutor.submit(task_info, logger, msg, extra)
            else:
                logger.info(msg=msg, extra=extra)


fount_logger = FountCustomLoggerClass.instance()
