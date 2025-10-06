from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth, messages
from django.urls import reverse

from users.authentication import CookieJWTAuthentication
from users.models import User
from users.forms import UserLoginForm, UserRegistrationForm, UserProfileForm
from products.models import Basket
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([CookieJWTAuthentication])
def login(request):
  if request.method == 'POST':
    form = UserLoginForm(data=request.POST)
    if form.is_valid():
      username = request.POST['username']
      password = request.POST['password']
      user = auth.authenticate(username=username, password=password)
      if user is None:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
      refresh = RefreshToken.for_user(user)
      response = HttpResponseRedirect(reverse('index'))
      response.set_cookie('refresh', refresh, httponly=True, max_age=3600)
      response.set_cookie('access', refresh.access_token, httponly=True, max_age=3600)
      if user:
        return response
  else:
    form = UserLoginForm()
  context = {'form': form}
  return render(request, 'users/login.html', context)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([CookieJWTAuthentication])
def registration(request):
  if request.method == 'POST':
    form = UserRegistrationForm(data=request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Вы успешно зарегистрировались!')
      return HttpResponseRedirect(reverse('users:login'))
  else:
    form = UserRegistrationForm()
  context = {'form': form}
  return render(request, 'users/registration.html', context)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def profile(request):
  if request.method == 'POST':
    form = UserProfileForm(instance=request.user, data=request.POST, files=request.FILES)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('users:profile'))
    else:
      print(form.errors)
  else:
    form = UserProfileForm(instance=request.user)

  baskets = Basket.objects.filter(user=request.user)
  total_sum = 0
  total_quantity = 0
  for basket in baskets:
    total_sum += basket.sum()
    total_quantity += basket.quantity

  context = {
    'title': 'Step_by_Step - Профиль',
    'form': form,
    'baskets': Basket.objects.filter(user=request.user),
    'total_sum': total_sum,
    'total_quantity': total_quantity,
  }
  return render(request, 'users/profile.html', context)


@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def logout(request):
  response = HttpResponseRedirect(reverse('index'))
  response.set_cookie('refresh', '', httponly=True, max_age=3600)
  response.set_cookie('access', '', httponly=True, max_age=3600)
  auth.logout(request)
  return response
