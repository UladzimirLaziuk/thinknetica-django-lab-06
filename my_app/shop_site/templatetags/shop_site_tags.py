from django import template
import random

from django.template.defaultfilters import stringfilter

register = template.Library()


@register.simple_tag
def random_int(int_range=100):
    return random.randint(1, int_range)


@register.filter
@stringfilter
def reverse_string(string_data):
    return string_data[::-1]
