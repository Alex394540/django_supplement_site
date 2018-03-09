from django import template

register = template.Library()

@register.filter(name='prepend_dollars')
def prepend_dollars(dollars):
    if isinstance(dollars, float):
        return "%.2f" % dollars
    return dollars