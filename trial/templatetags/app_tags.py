from trial.models import GlobalChecker
from django import template

register = template.Library()

@register.simple_tag
def check_new_orders():
    return GlobalChecker.objects.get(pk=1).new_orders