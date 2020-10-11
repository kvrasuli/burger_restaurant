from foodcartapp.models import RestaurantMenuItem
import requests
from geopy import distance
from StarBurger.settings import YANDEX_GEO_API_KEY


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


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(restaurant_address, order_address):
    try:
        restaurants_coords = fetch_coordinates(
            YANDEX_GEO_API_KEY, restaurant_address
        )
        order_coords = fetch_coordinates(
            YANDEX_GEO_API_KEY, order_address
        )
    except requests.exceptions.HTTPError:
        pass
    return distance.distance(
        (restaurants_coords[1], restaurants_coords[0]),
        (order_coords[1], order_coords[0]),
    ).km
