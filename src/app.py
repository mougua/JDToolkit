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
    # jd.price_protect("59856764134","1040870")


def handle_order_list(soup):
    table = soup.find(class_='order-tb')
    order_list = table('tbody')
    for order in order_list:
        items = []
        order_status = order.find(class_='order-status')
        if order_status and str.strip(order_status.string) == '已完成':
            deal_time = order.find(class_='dealtime').string
            if deal_time:
                deal_time = parse_ymd(deal_time)
                order_tag = order.find(attrs={'name': 'orderIdLinks'})
                if order_tag:
                    print(deal_time)
                    order_id = order_tag.string
                    print(order_id)
                    items_tag = order.find_all(class_='goods-item')
                    # 循环一张订单里面的商品
                    total_price = 0.0
                    for item_tag in items_tag:
                        item_id = item_tag['class'][1][2:]
                        items.append(item_id)
                        goods_number_tag = item_tag.parent.find(class_='goods-number')
                        goods_number = int(
                            str.strip(goods_number_tag.string.replace('x', ''))) if goods_number_tag else 0
                        price = jd.get_current_price(item_id)
                        total_price += price * goods_number
                        print(item_id, price, goods_number)
                    total_price = total_price + 6 if total_price < 99 else total_price  # 加上运费

                    # 现价
                    amount_tag = order.find(class_='amount')
                    amount = float(amount_tag.find('span').string[4:]) if amount_tag else 0
                    print('现价', total_price)
                    print('当时价', amount)
                    if (amount > total_price):
                        for itm in items:
                            jd.price_protect(order_id, itm)
                    print('\n')


if __name__ == '__main__':
    os.system('touch %s' % COOKIES_FILE)
    app()
