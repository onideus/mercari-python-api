from mercari import Mercari

mercari_api = Mercari()

print('_' * 80)
# print(mercari_api.name)
# print(mercari_api.fetch_all_items(keyword='ps5'))
# print(mercari_api.get_item_info('https://www.mercari.com/us/item/m59419748588/'))

for item in mercari_api.fetch_all_items_from_profile(563891995):
    print(mercari_api.get_item_info(item))

