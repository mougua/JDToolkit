import json

import requests

COOKIES_FILE = 'jd.cookies'
ORDER_LIST_KEYWORD = '我的订单'
LOGIN_REQ = "欢迎登录"


def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        txt = tag[index].get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag[index].text
        return txt.strip(' \t\r\n') if txt else ''


def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        txt = tag.get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag.text
        return txt.strip(' \t\r\n') if txt else ''


def print_json(resp_text):
    '''
    format the response content
    '''
    if resp_text[0] == '(':
        resp_text = resp_text[1:-1]

    for k, v in json.loads(resp_text).items():
        print(u'%s : %s' % (k, v))


def response_status(resp):
    if resp.status_code != requests.codes.OK:
        print('Status: %u, Url: %s' % (resp.status_code, resp.url))
        return False
    return True


def print_tty(binary_array):
    import sys
    out = sys.stdout
    modcount = len(binary_array)
    out.write("\x1b[1;47m" + (" " * (modcount * 2 + 4)) + "\x1b[0m\n")
    for r in range(modcount):
        out.write("\x1b[1;47m  \x1b[40m")
        for c in range(modcount):
            if binary_array[r][c]:
                out.write("  ")
            else:
                out.write("\x1b[1;47m  \x1b[40m")
        out.write("\x1b[1;47m  \x1b[0m\n")
    out.write("\x1b[1;47m" + (" " * (modcount * 2 + 4)) + "\x1b[0m\n")
    out.flush()
