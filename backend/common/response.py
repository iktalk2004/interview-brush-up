"""
自定义响应类
"""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message='success', code=200, http_status=status.HTTP_200_OK):
    """
    成功响应
    """
    return Response({
        'code': code,
        'message': message,
        'data': data,
    }, status=http_status)


def error_response(message='error', code=400, data=None, http_status=status.HTTP_400_BAD_REQUEST):
    """
    错误响应
    """
    return Response({
        'code': code,
        'message': message,
        'data': data,
    }, status=http_status)


def created_response(data=None, message='创建成功'):
    """
    创建成功响应
    """
    return success_response(data=data, message=message, code=201, http_status=status.HTTP_201_CREATED)


