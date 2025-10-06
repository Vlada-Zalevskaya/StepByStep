import stripe
from http import HTTPStatus

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from users.authentication import CookieJWTAuthentication
from common.views import TitleMixin
from orders.forms import OrderForm
from products.models import Basket
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessTemplateView(TitleMixin, TemplateView):
  template_name = 'orders/success.html'
  title = 'Step-by-Step - Спасибо за заказ!'


class CanceledTemplateView(TemplateView):
  template_name = 'orders/cancled.html'


class OrderListView(TitleMixin, ListView):
  template_name = 'orders/orders.html'
  title = 'Step-by-Step - Заказы'
  queryset = Order.objects.all()
  ordering = ('-created')
  permission_classes([IsAuthenticated])
  authentication_classes([CookieJWTAuthentication])
  api_view(['GET'])

  def get_queryset(self):
    queryset = super(OrderListView, self).get_queryset()
    return queryset.filter(initiator=self.request.user)


class OrderDetailView(DetailView):
  template_name = 'orders/order.html'
  model = Order

  api_view(['GET'])
  permission_classes([IsAuthenticated])
  authentication_classes([CookieJWTAuthentication])
  def get_context_data(self, **kwargs):
    context = super(OrderDetailView, self).get_context_data(**kwargs)
    context['title'] = f'Store - Заказ #{self.object.id}'
    return context


class OrderCreateView(TitleMixin, CreateView):
  template_name = 'orders/order-create.html'
  form_class = OrderForm
  success_url = reverse_lazy('orders:order_create')
  title = 'Step-by-Step - Оформление заказа'
  authentication_classes([CookieJWTAuthentication])
  api_view(['POST'])
  permission_classes([IsAuthenticated])

  def post(self, request, *args, **kwargs):
    super(OrderCreateView, self).post(request, *args, **kwargs)
    baskets = Basket.objects.filter(user=self.request.user)

    checkout_session = stripe.checkout.Session.create(
      line_items=baskets.stripe_products(),
      metadata={'order_id': self.object.id},
      mode='payment',
      success_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_success')),
      cancel_url='{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_canceled')),
    )
    return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

  def form_valid(self, form):
    form.instance.initiator = self.request.user
    return super(OrderCreateView, self).form_valid(form)


@csrf_exempt
def stripe_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
  except ValueError:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError:
    # Invalid signature
    return HttpResponse(status=400)

  # Handle the checkout.session.completed event
  if event['type'] == 'checkout.session.completed':
    session = event['data']['object']

    # Fulfill the purchase...
    fulfill_order(session)

  # Passed signature verification
  return HttpResponse(status=200)


def fulfill_order(session):
  order_id = int(session.metadata.order_id)
  order = Order.objects.get(id=order_id)
  order.update_after_payment()
