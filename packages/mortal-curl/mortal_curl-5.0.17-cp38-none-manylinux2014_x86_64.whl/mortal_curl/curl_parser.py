#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Author: MaJian
@Time: 2025/5/26 15:46
@SoftWare: PyCharm
@Project: mortal
@File: parser.py
"""
import json

import ply.yacc as yacc

from .curl_lexer import CurlLexer


class CurlParser:
    """curl命令语法分析器类"""

    def __init__(self, debug=False):
        self._result = None
        self.debug = debug
        self.lexer = CurlLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=self.debug)

    def parse(self, data):
        result = self.parser.parse(input=data, lexer=self.lexer.lexer)
        self._parse_result(result.get("options"))
        return result

    def _parse_result(self, result):
        content_type = 'Content-Type'
        urlencoded_type = 'application/x-www-form-urlencoded'
        json_type = 'application/json'
        self._result = dict()
        for attr in ["url", "method", "params", "headers", "data", "json", "auth", "form", "cookies", "compressed"]:
            if result.get(attr):
                self._result.update({attr: result.get(attr)})
        if result.get("verify") is False:
            self._result.update({"verify": False})
        data_type = result.get("data_type")
        headers = self._result.get("headers") or {}
        if headers.get(content_type.lower()):
            headers.update({content_type: headers.pop(content_type.lower())})
        content_type_str = headers.get(content_type, '')
        if data_type == "data":
            if not content_type_str:
                headers.update({content_type: urlencoded_type})
                self._result.update({"headers": headers})
            if not self._result.get("method"):
                self._result.update({"method": "POST"})
        elif data_type == "binary":
            self._result.update({"method": "POST"})
        elif data_type == "urlencode":
            headers.update({content_type: urlencoded_type})
            self._result.update({"headers": headers})
            self._result.update({"method": "POST"})
        if self._result.get("data") and json_type in content_type_str:
            pop_data = self._result.pop("data")
            if """\\\'""" in pop_data:
                pop_data = pop_data.replace("""\\\'""", "'")
            self._result.update({"json": json.loads(pop_data)})
        if not self._result.get("method"):
            self._result.update({"method": "GET"})
        self.__dict__.update(self._result)

    def dict(self):
        return self._result

    def pretty(self, indent=4):
        return json.dumps(self._result, indent=indent, ensure_ascii=False)

    # -------------------- 语法规则方法 --------------------
    def p_curl_command(self, p):
        """curl_command : CURL options"""
        p[0] = {'command': 'curl', 'options': p[2]}

    def p_options(self, p):
        """options : options option
                   | option"""
        if len(p) == 3:
            if isinstance(p[1], dict) and isinstance(p[2], dict):
                # 合并头部信息
                if 'headers' in p[1] and 'headers' in p[2]:
                    p[1]['headers'].update(p[2]['headers'])
                    p[0] = p[1]
                else:
                    p[0] = {**p[1], **p[2]}
            else:
                p[0] = p[1]
        else:
            p[0] = p[1]

    def p_option(self, p):
        """option : request_option
                  | header_option
                  | binary_option
                  | urlencode_option
                  | data_option
                  | form_option
                  | get_option
                  | user_option
                  | insecure_option
                  | params_option
                  | cookie_option
                  | compress_option
                  | url_option"""
        p[0] = p[1]

    def p_request_option(self, p):
        """request_option : REQUEST_OPT STRING
                          | REQUEST_OPT QUOTED_STRING"""
        p[0] = {'method': p[2].upper()}

    def p_header_option(self, p):
        """header_option : HEADER_OPT HEADER
                         | HEADER_OPT QUOTED_STRING"""
        if ':' in p[2]:
            key, value = p[2].split(':', 1)
            if 'sec-ch-ua' not in key.lower() and 'sec-fetch-' not in key.lower() and 'priority' not in key.lower():
                p[0] = {'headers': {key.strip(): value.strip()}}
        else:
            p[0] = {'headers': {p[2]: ''}}

    def p_binary_option(self, p):
        """binary_option : BINARY_OPT STRING
                         | BINARY_OPT QUOTED_STRING"""
        p[0] = {'data': p[2], 'data_type': 'binary'}

    def p_urlencode_option(self, p):
        """urlencode_option : URLENCODE_OPT STRING
                            | URLENCODE_OPT QUOTED_STRING"""
        p[0] = {'data': p[2], 'data_type': 'urlencode'}

    def p_data_option(self, p):
        """data_option : DATA_OPT STRING
                       | DATA_OPT QUOTED_STRING"""
        p[0] = {'data': p[2], 'data_type': 'data'}

    def p_form_option(self, p):
        """form_option : FORM_OPT FORM_DATA
                       | FORM_OPT STRING
                       | FORM_OPT QUOTED_STRING"""
        if '@' in p[2]:
            field, filename = p[2].split('@', 1)
            p[0] = {'form': {field: f'@{filename}'}}
        else:
            p[0] = {'form': p[2]}

    def p_get_option(self, p):
        """get_option : GET_OPT"""
        p[0] = {'method': 'GET'}

    def p_user_option(self, p):
        """user_option : USER_OPT STRING
                       | USER_OPT USER_CRED
                       | USER_OPT QUOTED_STRING"""
        if ':' in p[2]:
            username, password = p[2].split(':', 1)
            p[0] = {'auth': {'username': username, 'password': password}}
        else:
            p[0] = {'auth': {'username': p[2]}}

    def p_insecure_option(self, p):
        """insecure_option : INSECURE_OPT"""
        p[0] = {'verify': False}

    def p_params_option(self, p):
        """params_option : PARAMS"""
        if '&' in p[1]:
            params = {}
            for item in p[1].split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    params[key] = value
            p[0] = {'params': params}
        else:
            if '=' in p[1]:
                key, value = p[1].split('=', 1)
                p[0] = {'params': {key: value}}

    def p_cookie_option(self, p):
        """cookie_option : COOKIE_OPT COOKIE
                         | COOKIE_OPT STRING
                         | COOKIE_OPT QUOTED_STRING"""
        if '=' in p[2]:
            key, value = p[2].split('=', 1)
            p[0] = {'cookies': {key: value}}
        else:
            p[0] = {'cookies': {'name': p[2]}}

    def p_compress_option(self, p):
        """compress_option : COMPRESS_OPT"""
        p[0] = {'compressed': True}

    def p_url_option(self, p):
        """url_option : URL"""
        p[0] = {'url': p[1]}

    def p_error(self, p):
        """语法错误处理方法"""
        if p:
            print(f"语法错误在 '{p.value}' (类型: {p.type}, 行: {p.lineno})")
        else:
            print("语法错误在文件结尾")
