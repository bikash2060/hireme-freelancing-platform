from googletrans import Translator
from django.conf import settings
from django.core.cache import cache
import hashlib

def get_translator():
    """Get or create a translator instance"""
    return Translator()

def translate_text(text, target_lang='ne'):
    """
    Translate text to target language with caching
    """
    if not text or target_lang == 'en':
        return text

    # Create a cache key based on the text and target language
    cache_key = f"trans_{hashlib.md5(f'{text}_{target_lang}'.encode()).hexdigest()}"
    
    # Try to get from cache first
    cached_translation = cache.get(cache_key)
    if cached_translation:
        return cached_translation

    try:
        translator = get_translator()
        translation = translator.translate(text, dest=target_lang)
        translated_text = translation.text
        
        # Cache the translation for 24 hours
        cache.set(cache_key, translated_text, 60 * 60 * 24)
        
        return translated_text
    except Exception as e:
        # If translation fails, return original text
        print(f"Translation error: {str(e)}")
        return text 