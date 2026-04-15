from django import template
import locale

register = template.Library()

@register.filter
def currency_xof(value):
    try:
        # Format with thousand separator and FCFA suffix
        if value is None:
            return "0 FCFA"
        
        # Simple formatting for FCFA
        formatted_value = "{:,.0f}".format(float(value)).replace(",", " ")
        return f"{formatted_value} FCFA"
    except (ValueError, TypeError):
        return f"{value} FCFA"
