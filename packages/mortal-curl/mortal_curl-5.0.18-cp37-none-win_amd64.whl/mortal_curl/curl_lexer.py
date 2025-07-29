#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author: MaJian
@Time: 2025/5/26 15:46
@SoftWare: PyCharm
@Project: mortal
@File: lexer.py
"""

import ply.lex as lex


class CurlLexer:
    """curl命令词法分析器类"""

    def __init__(self):
        self._build_tokens()
        self.lexer = lex.lex(module=self)

    def _build_tokens(self):
        self.tokens = (
            'CURL',
            'REQUEST_OPT',  # -X/--request
            'HEADER_OPT',  # -H/--header
            'DATA_OPT',  # -d/--data/--data-ascii/--data-raw
            'BINARY_OPT',  # --data-binary
            'URLENCODE_OPT',  # --data-urlencode
            'FORM_OPT',  # -F/--form
            'GET_OPT',  # -G/--get
            'USER_OPT',  # -u/--user
            'INSECURE_OPT',  # -k/--insecure
            'COOKIE_OPT',  # -b/--cookie
            'COMPRESS_OPT',  # --compressed
            'URL',
            'PARAMS',
            'HEADER',
            'FORM_DATA',
            'USER_CRED',
            'COOKIE',
            'STRING',
            'QUOTED_STRING',
        )

    # -------------------- 词法规则方法 --------------------
    def t_CURL(self, t):
        r"""curl\b"""
        return t

    def t_REQUEST_OPT(self, t):
        r"""-(X)|--(request)\b"""
        return t

    def t_HEADER_OPT(self, t):
        r"""-(H)|--(header)\b"""
        return t

    def t_BINARY_OPT(self, t):
        r"""--(data-binary)\b"""
        return t

    def t_URLENCODE_OPT(self, t):
        r"""--(data-urlencode)\b"""
        return t

    def t_DATA_OPT(self, t):
        r"""-(d)|--(data(-ascii)?(-raw)?)\b"""
        return t

    def t_FORM_OPT(self, t):
        r"""-(F)|--(form)\b"""
        return t

    def t_GET_OPT(self, t):
        r"""-(G)|--(get)\b"""
        return t

    def t_USER_OPT(self, t):
        r"""-(u)|--(user)\b"""
        return t

    def t_INSECURE_OPT(self, t):
        r"""-(k)|--(insecure)\b"""
        return t

    def t_COOKIE_OPT(self, t):
        r"""-(b)|--(cookie)\b"""
        return t

    def t_COMPRESS_OPT(self, t):
        r"""--(compressed)\b"""
        return t

    def t_URL(self, t):
        r"""\"(https?|ftp)://[^\?\s]+|\'(https?|ftp)://[^\?\s]+"""
        t.value = t.value[1:-1] if t.value.endswith('"') or t.value.endswith("'") else t.value[1:]
        return t

    def t_PARAMS(self, t):
        r"""\?[^\s]+"""
        t.value = t.value[1:-1] if t.value.endswith('"') or t.value.endswith("'") else t.value[1:]
        return t

    def t_HEADER(self, t):
        r"""[a-zA-Z\-]+:\s*[^\r\n]+"""
        t.value = t.value.strip()
        return t

    def t_FORM_DATA(self, t):
        r"""[^@\s]+@[^\s]+"""
        return t

    def t_USER_CRED(self, t):
        r"""\([^:\s]+:[^:\s]+\)"""
        t.value = t.value[1:-1]
        return t

    def t_COOKIE(self, t):
        r"""[^=\s]+=[^=\s]+"""
        return t

    def t_QUOTED_STRING(self, t):
        r"""\"([^\\\"]|\\.)*\"|\'([^\\\']|\\.)*\'"""
        t.value = t.value[1:-1]
        return t

    def t_STRING(self, t):
        r"""[^\s\'\"]+"""
        if t.value not in ("\\", "\\\\", '$'):
            return t

    # 忽略的字符
    t_ignore = ' \t\r\n'

    def t_newline(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        """错误处理"""
        print(f"非法字符 '{t.value[0]}'")
        t.lexer.skip(1)

    def tokenize(self, data):
        """
        对输入数据进行词法分析

        Args:
            data: 要分析的字符串数据

        Returns:
            生成的token迭代器
        """
        self.lexer.input(data)
        return self.lexer
