from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def endswith(value, arg):
    """
    Check if a string ends with the specified argument
    Usage: {{ value|endswith:arg }}
    """
    if value is None:
        return False
    return value.endswith(arg)

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return None

@register.filter
def div(value, arg):
    """
    Divides the value by the argument
    Usage: {{ value|div:arg }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """
    Multiplies the value by the argument
    Usage: {{ value|mul:arg }}
    """
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def percentage(value, arg):
    """
    Calculates percentage
    Usage: {{ value|percentage:arg }}
    """
    try:
        return float(value) / float(arg) * 100
    except (ValueError, ZeroDivisionError):
        return 0
        
@register.filter
def split(value, arg):
    """
    Splits a string by the specified delimiter
    Usage: {{ value|split:"," }}
    """
    if value is None:
        return []
    return value.split(arg)

@register.filter(is_safe=True)
def status_badge(status):
    """
    Returns a beautifully formatted badge for customer status
    Usage: {{ customer.status|status_badge }}
    """
    if not status:
        return mark_safe('<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"><i class="fas fa-question-circle mr-1"></i> No Status</span>')

    status_config = {
        'INVALID': {
            'bg_color': 'bg-red-100',
            'text_color': 'text-red-800',
            'icon': 'fas fa-times-circle',
            'label': 'Invalid'
        },
        'VALID': {
            'bg_color': 'bg-green-100',
            'text_color': 'text-green-800',
            'icon': 'fas fa-check-circle',
            'label': 'Valid'
        },
        'CALL_NOT_ATTENDED': {
            'bg_color': 'bg-yellow-100',
            'text_color': 'text-yellow-800',
            'icon': 'fas fa-phone-slash',
            'label': 'Call Not Attended'
        },
        'PLAN_PRESENTED': {
            'bg_color': 'bg-purple-100',
            'text_color': 'text-purple-800',
            'icon': 'fas fa-file-alt',
            'label': 'Plan Presented'
        },
        'INTERESTED': {
            'bg_color': 'bg-blue-100',
            'text_color': 'text-blue-800',
            'icon': 'fas fa-thumbs-up',
            'label': 'Interested'
        },
        'NOT_INTERESTED': {
            'bg_color': 'bg-gray-100',
            'text_color': 'text-gray-800',
            'icon': 'fas fa-thumbs-down',
            'label': 'Not Interested'
        },
        'FOLLOW_UP': {
            'bg_color': 'bg-indigo-100',
            'text_color': 'text-indigo-800',
            'icon': 'fas fa-calendar-check',
            'label': 'Follow Up'
        },
        'SHORTLISTED': {
            'bg_color': 'bg-green-100',
            'text_color': 'text-green-800',
            'icon': 'fas fa-star',
            'label': 'Shortlisted'
        },
        'CAMPUS_VISIT': {
            'bg_color': 'bg-orange-100',
            'text_color': 'text-orange-800',
            'icon': 'fas fa-building',
            'label': 'Campus Visit'
        },
        'REGISTRATION': {
            'bg_color': 'bg-teal-100',
            'text_color': 'text-teal-800',
            'icon': 'fas fa-clipboard-list',
            'label': 'Registration'
        },
        'ADMISSION': {
            'bg_color': 'bg-pink-100',
            'text_color': 'text-pink-800',
            'icon': 'fas fa-graduation-cap',
            'label': 'Admission'
        }
    }

    config = status_config.get(status, {
        'bg_color': 'bg-gray-100',
        'text_color': 'text-gray-800',
        'icon': 'fas fa-question-circle',
        'label': status
    })

    return mark_safe(
        f'<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium {config["bg_color"]} {config["text_color"]}">' +
        f'<i class="{config["icon"]} mr-1"></i> {config["label"]}' +
        f'</span>'
    )

@register.simple_tag
def status_icon(status):
    """
    Returns just the icon for a status
    Usage: {% status_icon customer.status %}
    """
    icons = {
        'INVALID': '<i class="fas fa-times-circle text-red-500"></i>',
        'VALID': '<i class="fas fa-check-circle text-green-500"></i>',
        'CALL_NOT_ATTENDED': '<i class="fas fa-phone-slash text-yellow-500"></i>',
        'PLAN_PRESENTED': '<i class="fas fa-file-alt text-purple-500"></i>',
        'INTERESTED': '<i class="fas fa-thumbs-up text-blue-500"></i>',
        'NOT_INTERESTED': '<i class="fas fa-thumbs-down text-gray-500"></i>',
        'FOLLOW_UP': '<i class="fas fa-calendar-check text-indigo-500"></i>',
        'SHORTLISTED': '<i class="fas fa-star text-green-500"></i>',
        'CAMPUS_VISIT': '<i class="fas fa-building text-orange-500"></i>',
        'REGISTRATION': '<i class="fas fa-clipboard-list text-teal-500"></i>',
        'ADMISSION': '<i class="fas fa-graduation-cap text-pink-500"></i>',
    }

    return mark_safe(icons.get(status, '<i class="fas fa-question-circle text-gray-500"></i>'))
