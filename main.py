import os
import csv
from time import time
from shutil import copyfile

from fetch import orders_obj
from logger import LOG

# fetch orders, transform it to csv and mail it to the recipient.

SHOW_DISCOUNT = bool(os.getenv("SHOW_DISCOUNT", False))
SEND_NOTIFICATION = bool(os.getenv("SEND_NOTIFICATION", True))
CHANNEL = os.getenv("CHANNEL", "CUSTOM")
PICKUP_ADDRESS_NAME = os.getenv("PICKUP_ADDRESS_NAME", "Mahaveer")
PICKUP_LOCATION_ID = int(os.getenv("PICKUP_LOCATION_ID", 1124203))

ID_PREFIX =  os.getenv("ID_PREFIX", "STY")
ID_FIRST_VALUE = int(os.getenv("ID_FIRST_VALUE", 238594550))
INFLUENCER_ID_PREFIX = os.getenv("INFLUENCER_ID_PREFIX", "ISTY")
INFLUENCER_COUPON_PREFIX = os.getenv("INFLUENCER_COUPON_PREFIX", "INFC")

DEFAULT_LENGTH = 10
DEFAULT_BREADTH = 10
DEFAULT_HEIGHT = 10
DEFAULT_WEIGHT = 0.5

SOURCE_FILE = 'order.csv'
DESTINATION_FILE = 'orders{}.csv'


def get_payment_method(payment_status):
    if payment_status == "PAID":
        return "Prepaid"
    elif payment_status == "AWAITING_PAYMENT":
        return "COD"

def get_order_date(date_string):
    date, time, _ = date_string.split(" ")
    year, month, day = date.split("-")
    hour, minute, _ = time.split(":")
    return f"{'-'.join([day, month, year])} {':'.join([hour, minute])}"


class IdGenerator(object):
    def __init__(self, ID_PREFIX=ID_PREFIX, INFLUENCER_ID_PREFIX=INFLUENCER_ID_PREFIX, ID_FIRST_VALUE=ID_FIRST_VALUE):
        
        self.id_prefix = ID_PREFIX
        self.id_first_value = ID_FIRST_VALUE
        self.influencer_id_prefix = INFLUENCER_ID_PREFIX

        LOG.debug(f"ID Prefix:{self.id_prefix}, Influencer ID Prefix:{self.influencer_id_prefix}, ID Last Value:{self.id_first_value}")


    def generate_id(self, ecwid_order_id):
        order_id = self.id_first_value + int(ecwid_order_id)

        if INFLUENCER_COUPON_PREFIX in order.get("discountCoupon", {}).get("code", "XXXX"): # Gracefully handling the discount coupon
            return f"{self.influencer_id_prefix}{order_id}"

        return f"{self.id_prefix}{order_id}"


if __name__ == "__main__":
    id_obj = IdGenerator()
    
    dest_file = DESTINATION_FILE.format(int(time()))
    copyfile(SOURCE_FILE, dest_file)

    
    for order in orders_obj.get_all_orders():
        order_id = id_obj.generate_id(order['id'])
        order_date = get_order_date(order['createDate'])
        channel = CHANNEL
        payment_method = get_payment_method(order['paymentStatus'])
        cutomer_first_name = order['shippingPerson'].get('firstName') or order['shippingPerson'].get('name')
        cutomer_last_name = order['shippingPerson'].get('lastName')
        # customer_name = order['shippingPerson']['name']
        customer_email = order['email']
        customer_mobile =  order['shippingPerson']['phone']
        customer_alternate_mobile = None
        address_line_1 = order['shippingPerson']['street']
        address_line_2 = None
        country =  order['shippingPerson']['countryName']
        state = order['shippingPerson']['stateOrProvinceName']
        city = order['shippingPerson']['city']
        pincode = order['shippingPerson']['postalCode'] 

        billing_address_line_1 = None
        billing_address_line_2 = None
        billing_country = None
        billing_state = None
        billing_city = None
        billing_pincode = None

        base_details = [order_id, order_date, channel, payment_method, cutomer_first_name, cutomer_last_name, customer_email, 
            customer_mobile, customer_alternate_mobile, address_line_1, address_line_2, country, state, city, pincode, 
            billing_address_line_1, billing_address_line_2, billing_country, billing_state, billing_city, billing_pincode]

        for item in order['items']:
            master_sku = item['sku']
            product_name = item['name']
            product_quantity = item['quantity']
            tax = item['tax'] if item['tax'] else None
            selling_price = item['price']
            discount = item.get('couponAmount') if SHOW_DISCOUNT else None
            shipping_charges = item.get('shipping') if item.get('shipping') else None
            cod_charges = None
            gift_wrap_charges = None
            total_discount_per_order = order['couponDiscount'] if SHOW_DISCOUNT else None
            length = item['dimensions']['length'] if item['dimensions']['length'] else DEFAULT_LENGTH
            breadth = item['dimensions']['width'] if item['dimensions']['width'] else DEFAULT_BREADTH
            height = item['dimensions']['height'] if item['dimensions']['height'] else DEFAULT_HEIGHT
            weight = item['weight'] if item['weight'] else DEFAULT_WEIGHT
            send_notification = SEND_NOTIFICATION
            comment = None
            hsn_code = None
            pickup_location_id = PICKUP_LOCATION_ID

            order_details = [master_sku, product_name, product_quantity, tax, selling_price, discount, shipping_charges, cod_charges,
                gift_wrap_charges, total_discount_per_order, length, breadth, height, weight, send_notification, comment, hsn_code, 
                pickup_location_id]

            total_detail = base_details + order_details
            with open(dest_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(total_detail)

        print(f"order id:{order_id}, order date: {order_date}, channel:{channel}, payment method:{payment_method}, customer email:{customer_email}, customer mobile:{customer_mobile}, order name:{order['items'][0].get('name')}")
