"""
自定义异常处理类
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    自定义异常处理函数
    """
    # 调用默认的异常处理函数
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_data = {
            'code': response.status_code,
            'message': _extract_message(response.data),
            'data': None,
        }
        response.data = custom_data
    else:
        if isinstance(exc, DjangoValidationError):
            data = {
                'code': 400,
                'message': str(exc.message) if hasattr(exc, 'message') else str(exc),
                'data': None,
            }
            response = Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.exception(f'Unexpected error: {exc}')
            data = {
                'code': 500,
                'message': '服务器内部错误',
                'data': None,
            }
            response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def _extract_message(data):
    """
    从异常数据中提取错误消息
    """
    if isinstance(data, dict):
        messages = []
        for key, value in data.items():
            if isinstance(value, list):
                messages.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                messages.append(f"{key}: {value}")
        return '; '.join(messages)
    elif isinstance(data, list):
        return ', '.join(str(item) for item in data)
    return str(data)













