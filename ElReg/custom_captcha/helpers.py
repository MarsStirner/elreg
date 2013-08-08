# -*- coding: utf-8 -*-
import random
from captcha.conf import settings


def math_challenge():
    operators = ('+', '*', '-',)
    operands = (random.randint(1, 10), random.randint(1, 10))
    operator = random.choice(operators)
    if operands[0] < operands[1] and '-' == operator:
        operands = (operands[1], operands[0])
    challenge = '%d%s%d' % (operands[0], operator, operands[1])
    challenge_view = '%d%s%d' % (operands[0], operator if operator != '*' else u"\u00D7", operands[1])
    return u'%s=' % (challenge_view), unicode(eval(challenge))