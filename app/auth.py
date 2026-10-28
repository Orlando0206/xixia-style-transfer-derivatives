# -*- coding: utf-8 -*-
"""用户认证：注册、登录。密码使用 PBKDF2 加盐哈希，不存明文。"""
import hashlib
import os
import sqlite3
from datetime import datetime

from .database import _conn


def _hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()


def register(username, password):
    username = (username or "").strip()
    if not username or not password:
        return False, "用户名和密码不能为空"
    if len(password) < 4:
        return False, "密码长度至少 4 位"
    conn = _conn()
    try:
        salt = os.urandom(16).hex()
        h = _hash(password, salt)
        conn.execute(
            "INSERT INTO users(username, password_hash, salt, created_at) "
            "VALUES(?,?,?,?)",
            (username, h, salt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        return True, "注册成功，请登录"
    except sqlite3.IntegrityError:
        return False, "用户名已存在"
    finally:
        conn.close()


def login(username, password):
    username = (username or "").strip()
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return False, "用户不存在", None
    if _hash(password, row["salt"]) == row["password_hash"]:
        return True, "登录成功", dict(row)
    return False, "密码错误", None
