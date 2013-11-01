# -*- coding: utf-8 -*-
import random
import re
from cStringIO import StringIO
from flask import make_response, session, abort
from application.app import app
from .conf import settings

try:
    import Image
    import ImageDraw
    import ImageFont
except ImportError:
    from PIL import Image, ImageDraw, ImageFont

NON_DIGITS_RX = re.compile('[^\d]')


@app.route('/static/captcha/<captcha_id>/', methods=['GET'])
def get_captcha_image(captcha_id):
    data = session.get('captcha_{id}'.format(id=captcha_id))
    if not data:
        abort(404)

    image = generate_image(data['challenge'])
    out = StringIO()
    image.save(out, "PNG")
    out.seek(0)
    response = make_response(out.read())
    response.headers['Content-Type'] = 'image/png'
    return response


def generate_image(text):
    if settings.CAPTCHA_FONT_PATH.lower().strip().endswith('ttf'):
        font = ImageFont.truetype(settings.CAPTCHA_FONT_PATH, settings.CAPTCHA_FONT_SIZE)
    else:
        font = ImageFont.load(settings.CAPTCHA_FONT_PATH)

    size = font.getsize(text)
    size = (size[0] * 2, int(size[1] * 2))
    image = Image.new('RGB', size, settings.CAPTCHA_BACKGROUND_COLOR)

    try:
        PIL_VERSION = int(NON_DIGITS_RX.sub('', Image.VERSION))
    except:
        PIL_VERSION = 116
    xpos = 2

    charlist = []
    for char in text:
        if char in settings.CAPTCHA_PUNCTUATION and len(charlist) >= 1:
            charlist[-1] += char
        else:
            charlist.append(char)
    for char in charlist:
        fgimage = Image.new('RGB', size, settings.CAPTCHA_FOREGROUND_COLOR)
        charimage = Image.new('L', size, '#000000')
        chardraw = ImageDraw.Draw(charimage)
        chardraw.text((8, 0), ' %s ' % char, font=font, fill='#ffffff')
        if settings.CAPTCHA_LETTER_ROTATION:
            if PIL_VERSION >= 116:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), expand=0, resample=Image.BICUBIC)
            else:
                charimage = charimage.rotate(random.randrange(*settings.CAPTCHA_LETTER_ROTATION), resample=Image.BICUBIC)
        box = charimage.getbbox()
        charimage = charimage.crop((box[0], box[1] - 4, box[2], box[3]))
        maskimage = Image.new('L', size)

        maskimage.paste(charimage, (xpos, 4, xpos + charimage.size[0], 4 + charimage.size[1]))
        size = maskimage.size
        image = Image.composite(fgimage, image, maskimage)
        xpos = xpos + 2 + charimage.size[0]

    image = image.crop((0, 0, xpos + 1, size[1]))
    draw = ImageDraw.Draw(image)

    for f in settings.noise_functions():
        draw = f(draw, image)
    for f in settings.filter_functions():
        image = f(image)

    return image