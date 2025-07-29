from django.http import HttpResponse
from django.shortcuts import render
from django.utils import translation

from smartestate.settings import *
from smartestate.functions import tuple_list_has_key


from config.models import Config

def home(request):
    # TODO: How to make it so that this does not need to be
    #       in every view?
    language = request.GET.get('language')
    if language is not None and tuple_list_has_key(LANGUAGES, language):
        translation.activate(language)
        request.session['language'] = language
    else:
        try:
            translation.activate(request.session['language'])
        except KeyError:
            translation.activate(translation.get_language())

    cover_text = Config.objects.get_or_create()[0].cover_text
    return render(request, 'smartestate/home.html', {
        "cover_text": cover_text,
        }
    )
