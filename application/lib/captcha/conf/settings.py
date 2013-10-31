# -*- coding: utf-8 -*-
import os
import sys
import config

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

CAPTCHA_FONT_PATH = getattr(config,
                            'CAPTCHA_FONT_PATH',
                            os.path.normpath(os.path.join(os.path.dirname(__file__), '../', 'fonts/Vera.ttf')))
CAPTCHA_FONT_SIZE = getattr(config, 'CAPTCHA_FONT_SIZE', 22)
CAPTCHA_LETTER_ROTATION = getattr(config, 'CAPTCHA_LETTER_ROTATION', (-15, 15))
CAPTCHA_BACKGROUND_COLOR = getattr(config, 'CAPTCHA_BACKGROUND_COLOR', '#ffffff')
CAPTCHA_FOREGROUND_COLOR = getattr(config, 'CAPTCHA_FOREGROUND_COLOR', '#001100')
CAPTCHA_CHALLENGE_FUNCT = getattr(config, 'CAPTCHA_CHALLENGE_FUNCT', 'captcha.helpers.math_challenge')
CAPTCHA_NOISE_FUNCTIONS = getattr(config,
                                  'CAPTCHA_NOISE_FUNCTIONS',
                                  ('captcha.helpers.noise_arcs', 'captcha.helpers.noise_dots',))
CAPTCHA_FILTER_FUNCTIONS = getattr(config, 'CAPTCHA_FILTER_FUNCTIONS', ('captcha.helpers.post_smooth',))
CAPTCHA_PUNCTUATION = getattr(config, 'CAPTCHA_PUNCTUATION', '''_"',.;:-''')
CAPTCHA_FLITE_PATH = getattr(config, 'CAPTCHA_FLITE_PATH', None)
CAPTCHA_TIMEOUT = getattr(config, 'CAPTCHA_TIMEOUT', 30)  # Minutes
CAPTCHA_LENGTH = int(getattr(config, 'CAPTCHA_LENGTH', 4))  # Chars
CAPTCHA_IMAGE_BEFORE_FIELD = getattr(config, 'CAPTCHA_IMAGE_BEFORE_FIELD', True)
CAPTCHA_DICTIONARY_MIN_LENGTH = getattr(config, 'CAPTCHA_DICTIONARY_MIN_LENGTH', 0)
CAPTCHA_DICTIONARY_MAX_LENGTH = getattr(config, 'CAPTCHA_DICTIONARY_MAX_LENGTH', 99)
if CAPTCHA_IMAGE_BEFORE_FIELD:
    CAPTCHA_OUTPUT_FORMAT = getattr(config, 'CAPTCHA_OUTPUT_FORMAT', u'%(image)s %(hidden_field)s %(text_field)s')
else:
    CAPTCHA_OUTPUT_FORMAT = getattr(config, 'CAPTCHA_OUTPUT_FORMAT', u'%(hidden_field)s %(text_field)s %(image)s')


# Failsafe
if CAPTCHA_DICTIONARY_MIN_LENGTH > CAPTCHA_DICTIONARY_MAX_LENGTH:
    CAPTCHA_DICTIONARY_MIN_LENGTH, CAPTCHA_DICTIONARY_MAX_LENGTH = CAPTCHA_DICTIONARY_MAX_LENGTH, CAPTCHA_DICTIONARY_MIN_LENGTH


def _callable_from_string(string_or_callable):
    if callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(__import__('.'.join(string_or_callable.split('.')[:-1]), {}, {}, ['']), string_or_callable.split('.')[-1])


def get_challenge():
    return _callable_from_string(CAPTCHA_CHALLENGE_FUNCT)


def noise_functions():
    if CAPTCHA_NOISE_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_NOISE_FUNCTIONS)
    return list()


def filter_functions():
    if CAPTCHA_FILTER_FUNCTIONS:
        return map(_callable_from_string, CAPTCHA_FILTER_FUNCTIONS)
    return list()
