from django import template

register = template.Library()

@register.filter
def currency_xof(value):
    if value is None or value == "":
        return "0 FCFA"
    try:
        # Just convert to int/float and add FCFA
        num = float(value)
        # Format with spaces as thousand separator manually to avoid locale issues
        formatted = "{:,.0f}".format(num).replace(",", " ")
        return f"{formatted} FCFA"
    except:
        return f"{value} FCFA"
