"""LibreTranslate integration for post translations."""

import requests
from flask import current_app
from flask_babel import _


def translate(text, source_language, dest_language):
    """Translate text through the configured LibreTranslate instance."""
    endpoint = current_app.config.get('LT_API_URL')
    if not endpoint:
        raise RuntimeError(_('Error: the translation service URL is not configured.'))

    payload = {
        'q': text,
        'source': source_language,
        'target': dest_language,
        'format': 'text',
    }
    api_key = current_app.config.get('LT_API_KEY')
    if api_key:
        payload['api_key'] = api_key

    try:
        response = requests.post(endpoint, json=payload, timeout=15)
        response.raise_for_status()
        translated = response.json().get('translatedText')
        if not isinstance(translated, str):
            raise ValueError('LibreTranslate response did not contain translatedText')
        return translated
    except (requests.RequestException, ValueError):
        current_app.logger.exception('LibreTranslate request failed')
        raise RuntimeError(_('Error: the translation service failed.'))
