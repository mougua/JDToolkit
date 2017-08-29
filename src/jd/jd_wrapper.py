import random
import time
from io import BytesIO

import bs4
from PIL import Image

from jd.utils import *
import pickle


class JDWrapper(object):
    def __init__(self, usr_name=None, usr_pwd=None):
        # cookie info
        self.track_id = ''
        self.uuid = ''
        self.eid = ''
        self.fp = ''

        self.usr_name = usr_name
        self.usr_pwd = usr_pwd

        self.interval = 0

        # init url related
        self.home = 'https://passport.jd.com/new/login.aspx'
        self.login = 'https://passport.jd.com/uc/loginService'
        self.image = 'https://authcode.jd.com/verify/image'
        self.auth = 'https://passport.jd.com/uc/showAuthCode'

        self.sess = requests.Session()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
        }

        self.cookies = {

        }

        self._load_cookies()

    def _save_cookies(self):
        with open(COOKIES_FILE, 'wb') as f:
            pickle.dump(self.cookies, f)

    def _load_cookies(self):
        try:
            with open(COOKIES_FILE, 'rb') as f:
                self.cookies = pickle.load(f)
        except Exception as e:
            print(e)
            return

    def login_by_qr(self):
        # jd login by QR code
        try:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print(u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )

            # step 1: open login page
            resp = self.sess.get(
                urls[0],
                headers=self.headers
            )
            resp.encoding = 'gbk'
            if resp.status_code != requests.codes.OK:
                print(u'获取登录页失败: %u' % resp.status_code)
                return False

            # save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # step 2: get QR image
            resp = self.sess.get(
                urls[1],
                headers=self.headers,
                cookies=self.cookies,
                params={
                    'appid': 133,
                    'size': 147,
                    't': int(time.time() * 1000)
                }
            )
            resp.encoding = 'gbk'
            if resp.status_code != requests.codes.OK:
                print(u'获取二维码失败: %u' % resp.status_code)
                return False

            # save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            # save QR code
            img_buf = BytesIO()
            resp.iter_content()
            for chunk in resp.iter_content(chunk_size=1024):
                img_buf.write(chunk)
            im = Image.open(img_buf)
            # scan QR code with phone
            mx, my = im.size
            # im.show()
            table = []
            for i in range(0, my, 3):
                row = []
                for j in range(0, mx, 3):
                    v = im.getpixel((i, j))
                    v = 1 if v == 0 else 0
                    row.append(v)
                table.append(row)
            print_tty(table)
            # step 3： check scan result
            # mush have
            self.headers['Host'] = 'qr.m.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            while retry_times:
                retry_times -= 1
                resp = self.sess.get(
                    urls[2],
                    headers=self.headers,
                    cookies=self.cookies,
                    params={
                        'callback': 'jQuery%u' % random.randint(100000, 999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': int(time.time() * 1000)
                    }
                )
                resp.encoding = 'gbk'
                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1 + 1:n2])

                if rs['code'] == 200:
                    print(u'{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    # print(u'{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)

            if not qr_ticket:
                print(u'二维码登陆失败')
                return False

            # step 4: validate scan result
            # must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = self.sess.get(
                urls[3],
                headers=self.headers,
                cookies=self.cookies,
                params={'t': qr_ticket},
            )
            resp.encoding = 'gbk'
            if resp.status_code != requests.codes.OK:
                print(u'二维码登陆校验失败: %u' % resp.status_code)
                return False

            # login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            print(u'登陆成功')
            self._save_cookies()
            return True

        except Exception as e:
            print('Exp:', e)
            raise

    def get_order_list(self, page):
        url = 'https://order.jd.com/center/list.action'
        resp = self.sess.get(
            url,
            cookies=self.cookies,
            params={
                'd': 1,
                's': 4096,
                'page': page
            }
        )
        resp.encoding = 'gbk'
        if resp.status_code != requests.codes.OK:
            print('获取订单列表失败')
            return None
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        print(soup.head.title.string)
        return soup

    def get_current_price(self, item_id):
        item_url = 'https://p.3.cn/prices/mgets?skuIds=J_%s' % item_id
        resp = self.sess.get(
            item_url
        )
        price = float(resp.json()[0]['p'])
        return 0 if not price or price < 0 else price
        # print('price', soup.find(class_='price').string)

    def price_protect(self, orderId, skuId):

        # urlStr = 'https://sitepp-fm.jd.com/rest/pricepro/listSkus'
        # payload = {
        #     'orderId': orderId
        # }
        # resp = self.sess.post(
        #     urlStr,
        #     data=payload
        # )
        # if resp.status_code != requests.codes.OK:
        #     print('申请价格保护失败')
        # else:
        #     print(resp.content)


        url = 'https://sitepp-fm.jd.com/rest/pricepro/skuProtectApply'
        payload = {
            'orderId': orderId,
            'skuId': skuId
        }
        resp = self.sess.post(
            url,
            data=payload,
            cookies=self.cookies
        )
        resp.encoding = 'gbk'
        if resp.status_code != requests.codes.OK:
            print('申请价格保护失败')
        else:
            print(resp.content)
