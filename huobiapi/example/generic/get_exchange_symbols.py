from huobi.client.generic import GenericClient
from huobi.utils import *


generic_client = GenericClient()
list_obj = generic_client.get_exchange_symbols()
if len(list_obj):
    for idx, row in enumerate(list_obj):
        if row.base_currency == 'btc' and row.quote_currency == 'usdt':
            row.print_object()



