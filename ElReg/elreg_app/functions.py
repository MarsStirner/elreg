# -*- coding: utf-8 -*-
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def floatValidation(s):
  where = s.find(',')
  if where != -1:
    s = s[:where] + '.' + s[(where+1):]
  try:
    if s.startswith('-'):
      raise SyntaxError
    s = float(s)
    s = abs(s)
    s = round(s, 2)
    return s
  except (ValueError, SyntaxError, TypeError):
    return 0


def integerValidation(s):
  try:
    if s.startswith('-'):
      raise SyntaxError
    s = int(s)
    return s
  except (ValueError, SyntaxError, TypeError):
    return 0
  

def stringValidation(s):
  w = []
  s = r'%s' % s
  w.append(s.find('<'))
  w.append(s.find('>'))
  w.append(s.find('\\'))
  w.append(s.find('script'))
  w.append(s.find('SELECT'))
  w.append(s.find('UPDATE'))
  w.append(s.find('ALTER'))
  w.append(s.find('DROP'))
  try:
    for i in list(xrange(6)):
      if w[i] == -1:
        continue
      else:
        raise SyntaxError
    return s
  except (ValueError, SyntaxError, TypeError):
    return 0

def emailValidation(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False
