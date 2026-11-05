# -*- coding: utf-8 -*-
"""Pure Python 2.7 PNG preview renderer. Uses demonstration values only."""
import base64
import struct
import zlib

WIDTH, HEIGHT = 900, 270
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

def _native_text(rows, x, y, value, font_size, color):
    """Use Windows GDI anti-aliased Arial, matching the GameFace font."""
    try:
        import ctypes
        from ctypes import wintypes
        gdi = ctypes.windll.gdi32

        class BitmapInfoHeader(ctypes.Structure):
            _fields_ = [('biSize', wintypes.DWORD), ('biWidth', wintypes.LONG),
                        ('biHeight', wintypes.LONG), ('biPlanes', wintypes.WORD),
                        ('biBitCount', wintypes.WORD), ('biCompression', wintypes.DWORD),
                        ('biSizeImage', wintypes.DWORD), ('biXPelsPerMeter', wintypes.LONG),
                        ('biYPelsPerMeter', wintypes.LONG), ('biClrUsed', wintypes.DWORD),
                        ('biClrImportant', wintypes.DWORD)]

        class BitmapInfo(ctypes.Structure):
            _fields_ = [('bmiHeader', BitmapInfoHeader), ('bmiColors', wintypes.DWORD * 3)]

        width, height = 620, max(75, font_size + 30)
        bmi = BitmapInfo()
        bmi.bmiHeader.biSize = ctypes.sizeof(BitmapInfoHeader)
        bmi.bmiHeader.biWidth = width
        bmi.bmiHeader.biHeight = -height
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0
        # Explicit pointer-width signatures are essential on the 64-bit WoT client.
        gdi.CreateCompatibleDC.restype = ctypes.c_void_p
        gdi.CreateCompatibleDC.argtypes = [ctypes.c_void_p]
        gdi.CreateDIBSection.restype = ctypes.c_void_p
        gdi.CreateFontW.restype = ctypes.c_void_p
        gdi.CreateFontW.argtypes = [ctypes.c_int] * 5 + [ctypes.c_uint] * 8 + [ctypes.c_wchar_p]
        gdi.SelectObject.restype = ctypes.c_void_p
        gdi.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        gdi.DeleteObject.argtypes = [ctypes.c_void_p]
        gdi.DeleteDC.argtypes = [ctypes.c_void_p]
        gdi.SetBkMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
        gdi.SetTextColor.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        gdi.TextOutW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_wchar_p, ctypes.c_int]
        gdi.CreateDIBSection.argtypes = [ctypes.c_void_p, ctypes.POINTER(BitmapInfo),
                                          ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p),
                                          ctypes.c_void_p, ctypes.c_uint]
        dc = gdi.CreateCompatibleDC(None)
        if not dc:
            return False
        bitmap = None
        font = None
        old_bmp = None
        old_font = None
        try:
            pixels = ctypes.c_void_p()
            bitmap = gdi.CreateDIBSection(dc, ctypes.byref(bmi), 0, ctypes.byref(pixels), None, 0)
            if not bitmap or not pixels.value:
                return False
            old_bmp = gdi.SelectObject(dc, bitmap)
            font = gdi.CreateFontW(-font_size, 0, 0, 0, 700, 0, 0, 0, 1,
                                   0, 0, 4, 0, u'Arial')
            if not font:
                return False
            old_font = gdi.SelectObject(dc, font)
            gdi.SetBkMode(dc, 1)
            gdi.SetTextColor(dc, 0x00FFFFFF)
            # The DIB starts black; white glyph coverage becomes grayscale alpha.
            value = unicode(value)
            gdi.TextOutW(dc, 0, 0, value, len(value))
            raw = ctypes.string_at(pixels.value, width * height * 4)
            # Trim to visible glyph bounds for accurate center alignment.
            min_x, max_x = width, -1
            for yy in range(min(height, font_size + 15)):
                start = yy * width * 4
                for xx in range(width):
                    if ord(raw[start + xx * 4]) > 8:
                        min_x = min(min_x, xx)
                        max_x = max(max_x, xx)
            if max_x < min_x:
                return True
            dx = int(x - (max_x - min_x + 1) / 2) - min_x
            dy = int(y)
            for yy in range(height):
                ry = dy + yy
                if ry < 0 or ry >= HEIGHT:
                    continue
                for xx in range(min_x, max_x + 1):
                    rx = dx + xx
                    if rx < 0 or rx >= WIDTH:
                        continue
                    a = ord(raw[(yy * width + xx) * 4])
                    if a < 3:
                        continue
                    dst = rx * 3
                    for ch in range(3):
                        old = rows[ry][dst + ch]
                        rows[ry][dst + ch] = (old * (255 - a) + color[ch] * a) // 255
            return True
        finally:
            if old_font:
                gdi.SelectObject(dc, old_font)
            if old_bmp:
                gdi.SelectObject(dc, old_bmp)
            if font:
                gdi.DeleteObject(font)
            if bitmap:
                gdi.DeleteObject(bitmap)
            gdi.DeleteDC(dc)
    except Exception:
        return False


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
    cx, cy = WIDTH//2, 43
    gray = (103,119,130)
    _rect(canvas, cx-65, cy, 48, 1, gray)
    _rect(canvas, cx+17, cy, 48, 1, gray)
    _rect(canvas, cx, cy-17, 1, 12, gray)
    _rect(canvas, cx, cy+6, 1, 13, gray)
    size = max(10, min(30, _number(s, 'armor_label_font_size', 16)))
    font_size = int(size * 1.6)
    pixels = max(2, min(6, int(round(font_size/7.0))))
    spacing = max(font_size + 7, 7*pixels+4)
    x = cx + int(_number(s, 'armor_label_x_offset', 0)*0.6)
    y = cy+15 + int(_number(s, 'armor_label_y_offset', 35)*0.5)
    color = (169,112,255) if s.get('colorblind', False) else (107,244,13)
    if rows and y + len(rows)*spacing > HEIGHT-10:
        y = max(10, HEIGHT-10-len(rows)*spacing)
    for i,value in enumerate(rows):
        if not _native_text(canvas, x, y+i*spacing, value, font_size, color):
            _text(canvas, x, y+i*spacing, value, pixels, color)
    raw = b''.join(b'\x00'+bytes(line) for line in canvas)
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', struct.pack('!2I5B', WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    png += _chunk(b'IDAT', zlib.compress(raw, 5))
    png += _chunk(b'IEND', b'')
    encoded = base64.b64encode(png)
    if not isinstance(encoded, str): encoded = encoded.decode('ascii')
    return 'data:image/png;base64,' + encoded
