# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/25 20:54
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
import os.path

from .api import (
    DATE_FORMAT,
    TIME_FORMAT,
    FILE,
    update,
    get_tradingdays,
    get_tradingtime,
    get_recent_reportdate,
    get_recent_tradeday,
    is_tradeday,
    is_reportdate,
    shift_tradeday,
    shift_tradedt,
    shift_tradetime,
    shift_reportdate,
    today,
    now,
)

__version__ = "v0.0.3"

if not os.path.exists(FILE):
    print(f"{FILE} missing")
    update()


__all__ = [
    "DATE_FORMAT",
    "TIME_FORMAT",
    "FILE",
    "update",
    "get_tradingdays",
    "get_tradingtime",
    "get_recent_reportdate",
    "get_recent_tradeday",
    "is_tradeday",
    "is_reportdate",
    "shift_tradeday",
    "shift_tradetime",
    "shift_tradedt",
    "shift_reportdate",
    "today",
    "now",
]
