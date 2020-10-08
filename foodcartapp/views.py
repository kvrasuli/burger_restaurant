from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from .models import Product, OrderItem, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'ingridients': product.ingridients,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['POST'])
def register_order(request):
    if 'products' not in request.data:
        return Response({'error': 'products key doesn\'t exist'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not request.data['products']:
        return Response({'error': 'products are empty'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not isinstance(request.data['products'], list):
        return Response({'error': 'products are not packed in a list'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not all(key in request.data for key in ('firstname', 'lastname', 'phonenumber', 'address')):
        return Response({'error': 'some of order keys don\'t exist'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not all(isinstance(request.data[key], str) for key in ('firstname', 'lastname', 'phonenumber', 'address')):
        return Response({'error': 'some of order parameters are not strings'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not all(request.data[key] for key in ('firstname', 'lastname', 'phonenumber', 'address')):
        return Response({'error': 'some of order parameters are empty'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    if not all(isinstance(request.data['products'][position][key], int) for key in ('product', 'quantity') for position in range(len(request.data['products']))):
        return Response({'error': 'wrong product id or quantity'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    order = Order.objects.create(
        firstname=request.data['firstname'],
        lastname=request.data['lastname'],
        phonenumber=request.data['phonenumber'],
        address=request.data['address']
    )
    for order_item in request.data['products']:
        product = Product.objects.get(id=order_item['product'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=order_item['quantity']
        )

    return Response({}, status=status.HTTP_201_CREATED)
