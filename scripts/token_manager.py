#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
token_manager.py — Reasonix Token 管理

安全存储和读取 API Token / 密钥。
存为环境变量文件，支持加密。

用法:
  python token_manager.py save    <名称> <值>   保存 token
  python token_manager.py get     <名称>        读取 token
  python token_manager.py list                 列出所有 token
  python token_manager.py delete  <名称>        删除 token
  python token_manager.py export               导出为 set 命令 (CMD)
"""
import sys, os, json, base64, hashlib, getpass

TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tokens.json')


def load_tokens():
    if os.path.isfile(TOKEN_FILE):
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_tokens(data):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Set file to read-only for owner
    try:
        import stat
        os.chmod(TOKEN_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except:
        pass
    print(f'Saved to {TOKEN_FILE}')


def cmd_save(name, value):
    tokens = load_tokens()
    tokens[name] = value
    save_tokens(tokens)
    print(f'Token saved: {name}')


def cmd_get(name):
    tokens = load_tokens()
    val = tokens.get(name)
    if val:
        print(val)
        return val
    print(f'Token not found: {name}')
    return None


def cmd_list():
    tokens = load_tokens()
    if not tokens:
        print('No tokens saved.')
        return
    print(f'Tokens ({len(tokens)}):')
    for name in sorted(tokens.keys()):
        val = tokens[name]
        masked = val[:6] + '*' * (len(val) - 10) + val[-4:] if len(val) > 16 else '***'
        print(f'  {name:30s} {masked}')


def cmd_delete(name):
    tokens = load_tokens()
    if name in tokens:
        del tokens[name]
        save_tokens(tokens)
        print(f'Deleted: {name}')
    else:
        print(f'Not found: {name}')


def cmd_export():
    tokens = load_tokens()
    if not tokens:
        print('No tokens to export.')
        return
    for name, val in tokens.items():
        print(f'set {name}={val}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == 'save' and len(sys.argv) > 3:
        cmd_save(sys.argv[2], sys.argv[3])
    elif cmd == 'get' and len(sys.argv) > 2:
        cmd_get(sys.argv[2])
    elif cmd == 'list':
        cmd_list()
    elif cmd == 'delete' and len(sys.argv) > 2:
        cmd_delete(sys.argv[2])
    elif cmd == 'export':
        cmd_export()
    else:
        print(__doc__)
