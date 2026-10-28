# -*- coding: utf-8 -*-
"""SQLite 数据库层：用户、历史记录、论坛帖子与回复。"""
import sqlite3
import os
import hashlib
from datetime import datetime

from . import config


def _conn():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            src_path TEXT NOT NULL,
            out_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_path TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS replies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )"""
    )
    conn.commit()
    conn.close()


# ---------- 历史记录 ----------
def add_history(user_id, task_type, src_path, out_path):
    conn = _conn()
    conn.execute(
        "INSERT INTO history(user_id, task_type, src_path, out_path, created_at) "
        "VALUES(?,?,?,?,?)",
        (user_id, task_type, src_path, out_path,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def list_history(user_id, limit=50):
    conn = _conn()
    rows = conn.execute(
        "SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- 论坛帖子 ----------
def add_post(user_id, title, content, image_path=""):
    conn = _conn()
    cur = conn.execute(
        "INSERT INTO posts(user_id, title, content, image_path, created_at) "
        "VALUES(?,?,?,?,?)",
        (user_id, title, content, image_path,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def list_posts(limit=100):
    conn = _conn()
    rows = conn.execute(
        """SELECT p.*, u.username FROM posts p
           JOIN users u ON u.id = p.user_id
           ORDER BY p.id DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_post(post_id):
    conn = _conn()
    row = conn.execute(
        """SELECT p.*, u.username FROM posts p
           JOIN users u ON u.id = p.user_id WHERE p.id=?""",
        (post_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_reply(post_id, user_id, content):
    conn = _conn()
    conn.execute(
        "INSERT INTO replies(post_id, user_id, content, created_at) "
        "VALUES(?,?,?,?)",
        (post_id, user_id, content,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def list_replies(post_id):
    conn = _conn()
    rows = conn.execute(
        """SELECT r.*, u.username FROM replies r
           JOIN users u ON u.id = r.user_id
           WHERE r.post_id=? ORDER BY r.id ASC""",
        (post_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_posts():
    conn = _conn()
    n = conn.execute("SELECT COUNT(*) AS c FROM posts").fetchone()["c"]
    conn.close()
    return n


def ensure_seed_user():
    """确保存在官方账号「西夏文化官微」，用于种子帖子，返回其 id。"""
    conn = _conn()
    row = conn.execute(
        "SELECT id FROM users WHERE username=?", ("西夏文化官微",)
    ).fetchone()
    if row:
        conn.close()
        return row["id"]
    salt = os.urandom(16).hex()
    # 随机密码，正常无法登录，仅用于展示
    pwd = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"),
                            salt.encode("utf-8"), 100000).hex()
    cur = conn.execute(
        "INSERT INTO users(username, password_hash, salt, created_at) "
        "VALUES(?,?,?,?)",
        ("西夏文化官微", h, salt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid
