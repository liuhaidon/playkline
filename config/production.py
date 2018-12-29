#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os

config = dict(
    DEBUG=True,
    # SITE_DOMAIN="http://www.vchits.com",
    log_path=os.path.join(os.path.dirname(__file__), "log"),  # 日志路径
    show_im=True,
    store_options={
        'redis_host': '127.0.0.1',
        'redis_port': 6380,
        'redis_pass': 'Deseka@2015',
    },
)
