from django import template
from django.utils.translation import get_language
from ..utils import translate_text

register = template.Library()

@register.simple_tag
def translate(text):
    """
    Template tag to translate text to the current language
    Usage: {% translate "Your text here" %}
    """
    current_lang = get_language()
    if current_lang == 'en':
        return text
    return translate_text(text, current_lang)

@register.filter
def translate_text_filter(text):
    """
    Template filter to translate text to the current language
    Usage: {{ "Your text here"|translate_text_filter }}
    """
    current_lang = get_language()
    if current_lang == 'en':
        return text
    return translate_text(text, current_lang) 