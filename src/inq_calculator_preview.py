# -*- coding: utf-8 -*-
"""Pure Python 2.7 PNG preview renderer. Uses demonstration values only."""
import base64
import struct
import zlib

WIDTH, HEIGHT = 600, 230
SLOT = 'inq_calculator_live_preview'
FONT = {
    '0': ('01110','10001','10011','10101','11001','10001','01110'),
    '1': ('00100','01100','00100','00100','00100','00100','01110'),
    '2': ('01110','10001','00001','00010','00100','01000','11111'),
    '3': ('11110','00001','00001','01110','00001','00001','11110'),
    '4': ('00010','00110','01010','10010','11111','00010','00010'),
    '5': ('11111','10000','10000','11110','00001','00001','11110'),
    '6': ('01110','10000','10000','11110','10001','10001','01110'),
    '7': ('11111','00001','00010','00100','01000','01000','01000'),
    '8': ('01110','10001','10001','01110','10001','10001','01110'),
    '9': ('01110','10001','10001','01111','00001','00001','01110'),
    '/': ('00001','00001','00010','00100','01000','10000','10000'),
    '%': ('11001','11010','00010','00100','01000','01011','10011'),
    ' ': ('00000',)*7,
    'G': ('01111','10000','10000','10111','10001','10001','01111'),
    'U': ('10001','10001','10001','10001','10001','10001','01110'),
    'N': ('10001','11001','10101','10101','10011','10001','10001'),
    u'°': ('01100','10010','01100','00000','00000','00000','00000'),
    u'†': ('00100','00100','11111','00100','00100','00100','00100'),
}

def _number(settings, key, default):
    try:
        return int(float(settings.get(key, default)))
    except (ValueError, TypeError):
        return default

def _rect(rows, x, y, w, h, color):
    x0, y0 = max(0, int(x)), max(0, int(y))
    x1, y1 = min(WIDTH, int(x+w)), min(HEIGHT, int(y+h))
    if x1 <= x0 or y1 <= y0:
        return
    rgb = bytes(bytearray(color))
    for yy in range(y0, y1):
        rows[yy][x0*3:x1*3] = rgb * (x1-x0)

def _text(rows, x, y, value, pixels, color):
    cursor = int(x - (len(value)*6-1)*pixels/2.0)
    for char in value:
        glyph = FONT.get(char, FONT[' '])
        for rowno, line in enumerate(glyph):
            for colno, on in enumerate(line):
                if on == '1':
                    _rect(rows, cursor+colno*pixels, y+rowno*pixels, pixels, pixels, color)
        cursor += 6*pixels

def _chunk(name, data):
    payload = name + data
    return struct.pack('!I', len(data)) + payload + struct.pack('!I', zlib.crc32(payload) & 0xffffffff)

def render_preview(settings):
    """Generate a data:image/png URI; does not contact the game or write files."""
    s = dict(settings or {})
    rows = []
    if s.get('armor_label_enabled', True): rows.append('250 / 230')
    if s.get('pen_label_enabled', False): rows.append('96%')
    if s.get('angle_label_enabled', False) and _number(s, 'angle_label_display_threshold', 65) <= 75: rows.append(u'75°')
    if s.get('eff_pen_label_enabled', False): rows.append('250')
    if s.get('kill_label_enabled', False): rows.append(u'† 75%')
    if s.get('gun_label_enabled', False): rows.append('GUN')
    canvas = [bytearray(b'\x14\x1a\x21' * WIDTH) for unused in range(HEIGHT)]
    _rect(canvas, 0, 0, WIDTH, 1, (66,78,91))
    _rect(canvas, 0, HEIGHT-1, WIDTH, 1, (66,78,91))
    cx, cy = WIDTH//2, 33
    gray = (103,119,130)
    _rect(canvas, cx-52, cy, 38, 1, gray)
    _rect(canvas, cx+14, cy, 38, 1, gray)
    _rect(canvas, cx, cy-17, 1, 12, gray)
    _rect(canvas, cx, cy+6, 1, 13, gray)
    size = max(10, min(30, _number(s, 'armor_label_font_size', 16)))
    pixels = max(2, min(4, int(round(size/7.0))))
    spacing = 7*pixels+5
    x = cx + int(_number(s, 'armor_label_x_offset', 0)*0.45)
    y = cy+13 + int(_number(s, 'armor_label_y_offset', 35)*0.35)
    color = (169,112,255) if s.get('colorblind', False) else (107,244,13)
    if rows and y + len(rows)*spacing > HEIGHT-10:
        y = max(10, HEIGHT-10-len(rows)*spacing)
    for i,value in enumerate(rows):
        _text(canvas, x, y+i*spacing, value, pixels, color)
    raw = b''.join(b'\x00'+bytes(line) for line in canvas)
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', struct.pack('!2I5B', WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    png += _chunk(b'IDAT', zlib.compress(raw, 5))
    png += _chunk(b'IEND', b'')
    encoded = base64.b64encode(png)
    if not isinstance(encoded, str): encoded = encoded.decode('ascii')
    return 'data:image/png;base64,' + encoded
