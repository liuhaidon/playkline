#!/usr/bin/env python
# -*- coding:utf-8 -*-
# ping++支付

import pingpp

# ping++ key,app_id
pingpp.api_key = 'sk_live_vjfbj9v58Sq5eXvbn11K88i5'
app_id = 'app_fLiD08XHmvLSnHGm'
url = 'http://playkline.com'

def payment(order_no, channel, amount, subject, body, ip):
    """支付"""
    ch = pingpp.Charge.create(
        order_no=order_no,  # 商户订单号
        channel=channel,  # 支付方式
        amount=amount,
        subject=subject,  # 商品名
        body=body,  # 商品描述
        currency='cny',
        app=dict(id=app_id),  # app_ID
        client_ip=ip,
        extra=dict(success_url=url+'/shop', cancel_url=url+'/shop')
    )
    return ch


def check():
    """查询"""
    pingpp.Charge.retrieve('CHARGE-ID')
    pingpp.Charge.all()


def refund():
    """退款"""
    ch = pingpp.Charge.retrieve('CHARGE-ID')
    re = ch.refunds.create()
    return ch, re


def refund_check():
    """退款查询"""
    ch = pingpp.Charge.retrieve('CHARGE-ID')
    re = ch.refunds.retrieve('REFUND-ID')
    ch = pingpp.Charge.retrieve('CHARGE-ID')
    re = ch.refunds.retrieve('REFUND-ID')
    return ch, re


def bribery_money_weixin():
    """微信红包"""
    pingpp.RedEnvelope.create()


def check_two():
    """查询"""
    pingpp.RedEnvelope.retrieve('RED-ID')
    pingpp.RedEnvelope.all()


def check_event():
    """查询event"""
    pingpp.Event.retrieve('RED-ID')


def check_list():
    """查询event列表"""
    pingpp.Event.all()


def weixin_entpay():
    """查询微信企业付款"""
    tr = pingpp.Transfer.create(
        order_no='1234567890',
        channel='wx_pub',
        amount=100,
        currency='cny',
        app=dict(id=app_id),
        type='b2c',
        recipient='youropenid',
        extra=dict(user_name='User Name', force_check=True),
        description='description'
    )
    return tr


def check_three():
    """查询"""
    pingpp.Transfer.retrieve('TR-ID')
    pingpp.Transfer.all()
