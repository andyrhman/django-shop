# core/signals.py
import datetime
import secrets

from django.dispatch import Signal, receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail

from decouple import config
from core.models import Token, Order, OrderItemStatus

# 1) define the signal; we'll send the Order instance whenever an order is completed
order_completed = Signal()

@receiver(order_completed)
def send_order_completed_email(sender, *, order: Order, **kwargs):
    """
    Fired when an order is marked completed. Gathers the order items,
    renders an email template, and sends out the notification.
    """
    # format order ID / total
    order_id = order.id
    order_total = f"Rp{order.total:,.0f}".replace(",", ".")  # Indonesian format
    
    # collect item data
    products = []
    for item in order.order_items_order.all():
        products.append({
            "title": item.product_title,
            "variant": item.variant.name if item.variant else "-",
            "price": f"Rp{item.price:,.0f}".replace(",", "."),
            "quantity": item.quantity,
            "image": item.product.image,
        })
    
    # render the HTML
    html_content = render_to_string(
        "order_completed.html",
        {
            "order_id": order_id,
            "order_total": order_total,
            "products": products,
        }
    )
    
    # send it
    send_mail(
        subject="Your order is complete 🎉",
        message="",  # HTML‐only
        from_email="service@mail.com",
        recipient_list=[order.email],
        html_message=html_content,
    )
