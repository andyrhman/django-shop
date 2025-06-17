import json
from pyexpat import model

from django.dispatch import Signal, receiver
from django.forms import model_to_dict
from django.template.loader import render_to_string
from django.core.mail import send_mail

from decouple import config
from app.producer import producer
from core.models import Order

order_completed = Signal()

@receiver(order_completed)
def send_order_completed_email(sender, *, order: Order, **kwargs):
    order_total = f"Rp{order.total:,.0f}".replace(",", ".")
    
    products = []
    for item in order.order_items_order.all():
        products.append({
            "title": item.product_title,
            "variant": item.variant.name if item.variant else "-",
            "price": f"Rp{item.price:,.0f}".replace(",", "."),
            "quantity": item.quantity,
            "image": item.product.image.url if item.product.image else "",
        })
        
    data = model_to_dict(order)
    data['order_total'] = order_total
    data['products'] = products

    payload = {
        "event": "order_completed",
        "order": data,
    }
    
    producer.send(config('KAFKA_TOPIC', default='default'), payload)
    producer.flush()
