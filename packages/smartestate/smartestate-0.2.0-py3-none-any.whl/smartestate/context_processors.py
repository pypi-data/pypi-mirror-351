from django.utils import translation
from .settings import VERSION, COPYRIGHT_TEXT, LANGUAGES


def smartestate_version(request):
    return {'VERSION': VERSION}


def copyright_text(request):
    return {'COPYRIGHT_TEXT': COPYRIGHT_TEXT}


def languages(request):
    return {'languages': LANGUAGES}


def current_language(request):
    try:
        current_language = request.session['language']
    except KeyError:
        current_language = translation.get_language()
    if current_language == "en-us":
        current_language = "en"
    return {'current_language': current_language}
