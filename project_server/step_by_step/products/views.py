from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth, messages
from django.urls import reverse

from products.models import ProductCategory, Product, Basket
from django.core.paginator import Paginator
from users.authentication import CookieJWTAuthentication


# Шаблоны.
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([CookieJWTAuthentication])
def index(request):  # контроллер
  context = {
    'title': 'Step-by-Step',
  }
  return render(request, 'products/index.html', context)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([CookieJWTAuthentication])
def products(request, category_id=None, page_number=1):
  products = Product.objects.filter(category_id=category_id) if category_id else Product.objects.all()
  per_page = 3
  paginator = Paginator(products, per_page)
  products_paginator = paginator.page(page_number)

  context = {
    'title': 'Step-by-Step - Каталог',
    'categories': ProductCategory.objects.all(),
    'products': products_paginator,
  }
  return render(request, 'products/products.html', context)


@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def basket_add(request, product_id):
  product = Product.objects.get(id=product_id)
  baskets = Basket.objects.filter(user=request.user, product=product)

  if not baskets.exists():
    Basket.objects.create(user=request.user, product=product, quantity=1)
  else:
    basket = baskets.first()
    basket.quantity += 1
    basket.save()

  return HttpResponseRedirect(request.META['HTTP_REFERER'])


@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def basket_remove(request, basket_id):
  basket = Basket.objects.get(id=basket_id)
  basket.delete()
  return HttpResponseRedirect(request.META['HTTP_REFERER'])
