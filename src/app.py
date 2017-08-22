from jd.jd_wrapper import *
import os

jd = JDWrapper()


def app():
    soup = jd.get_order_list(1)
    if soup.head.title.string.find(ORDER_LIST_KEYWORD) < 0:
        if not jd.login_by_qr():
            return
        soup = jd.get_order_list(1)
    handle_order_list(soup)


def handle_order_list(soup):
    table = soup.find(class_='order-tb')
    order_list = table('tbody')
    for order in order_list:
        deal_time = order.find(class_='dealtime').string
        order_tag = order.find(attrs={'name': 'orderIdLinks'})
        if order_tag:
            order_id = order_tag.string
            print(order_id)

            items_tag = order.find_all(class_='goods-item')
            for item_tag in items_tag:
                item_id = item_tag['class'][1][2:]
                jd.get_current_price(item_id)

            amount_tag = order.find(class_='amount')
            amount = amount_tag.find('span').string[4:] if amount_tag else 0
            print('amount', amount)
            print('\n')


if __name__ == '__main__':
    os.system('touch %s' % COOKIES_FILE)
    app()
