from foodcartapp.models import RestaurantMenuItem
import requests
from geopy import distance
from django.conf import settings
from django.core.cache import cache
from contextlib import suppress


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
    return set.intersection(*restaurants_for_order)



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
    with suppress(requests.exceptions.HTTPError):
        restaurants_coords = get_coordinates(restaurant_address)
        order_coords = fetch_coordinates(
            settings.YANDEX_GEO_API_KEY, order_address
        )
    return distance.distance(
        (restaurants_coords[1], restaurants_coords[0]),
        (order_coords[1], order_coords[0]),
    ).km


def get_coordinates(address):
    coordinates = cache.get(address)
    if not coordinates:
        coordinates = fetch_coordinates(settings.YANDEX_GEO_API_KEY, address)
        cache.set(address, coordinates, timeout=600)
    return coordinates
