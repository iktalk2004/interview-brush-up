import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code():
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_code(email):
    """发送验证码到邮箱"""
    # 检查发送间隔
    interval_key = f'verify_interval:{email}'
    if cache.get(interval_key):
        return False, '请稍后再试，验证码发送过于频繁'

    code = generate_verification_code()

    # 存入缓存
    code_key = f'verify_code:{email}'
    cache.set(code_key, code, settings.VERIFICATION_CODE_EXPIRE)
    cache.set(interval_key, True, settings.VERIFICATION_CODE_INTERVAL)

    # 发送邮件
    try:
        send_mail(
            subject='八股文刷题系统 - 验证码',
            message=f'您的验证码为：{code}，有效期5分钟。请勿泄露给他人。',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return True, '验证码已发送'
    except Exception as e:
        cache.delete(code_key)
        cache.delete(interval_key)
        return False, f'邮件发送失败：{str(e)}'


def verify_code(email, code):
    """校验验证码"""
    code_key = f'verify_code:{email}'
    cached_code = cache.get(code_key)

    if not cached_code:
        return False, '验证码已过期'

    if cached_code != code:
        return False, '验证码错误'

    cache.delete(code_key)
    return True, '验证成功'