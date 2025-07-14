# library/templatetags/custom_tags.py

from django import template

register = template.Library()

@register.filter
def has_paid(user, ebook):
    return ebook in user.paid_ebooks.all()
