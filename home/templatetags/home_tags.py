from django import template
from home.models import Footer

register = template.Library()


@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    """
    Template tag for footer snippet
    """
    return {
        'footer': Footer.objects.first(),  # there should be only one footer
        'request': context['request'],
    }
