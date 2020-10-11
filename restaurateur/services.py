from foodcartapp.models import RestaurantMenuItem


def get_restaurants(order):
    restaurants_for_order = []
    for order_item in order.items.prefetch_related('product'):
        restauraunts_for_item = set()
        menu_items = RestaurantMenuItem.objects.filter(
            product=order_item.product
        ).prefetch_related('restaurant')
        for menu_item in menu_items:
            restauraunts_for_item.add(menu_item.restaurant)
        restaurants_for_order.append(restauraunts_for_item)
    common_restaurants_for_order = set.intersection(*restaurants_for_order)
    if common_restaurants_for_order:
        return common_restaurants_for_order
    return ('Подходящих ресторанов нет!',)