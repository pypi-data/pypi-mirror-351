from ..common import load_packaging_types

order_number_allowed_fields = ['12NC', 'Alias', 'Status', 'Code', 'Type', 'Qty', 'PackagingData']

def validate_order_number_fields(part):
    for order_number in part['orderNumbers']:
        order = part['orderNumbers'][order_number]
        for field in order:
            if field not in order_number_allowed_fields:
                return False

        if not validate_packaging_type(order):
            return False
    return True


def validate_packaging_type(order_number):
    if 'Type' in order_number:
        if order_number['Type'] not in load_packaging_types():
            return False
    return True