from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    if pattern_or_urlname != 'home':
        if pattern_or_urlname in context['request'].path:
            return 'active'
        return ''
    else:
        path = context['request'].path
        if path == '/':
            return 'active'
        return ''
