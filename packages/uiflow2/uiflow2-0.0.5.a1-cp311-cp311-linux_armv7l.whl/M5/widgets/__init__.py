# SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

import M5



def fillScreen(color):
    stash_color = M5.Lcd.getRawColor()
    M5.Lcd.setColor(color)
    M5.Lcd.fillScreen()
    M5.Lcd.setRawColor(stash_color)

def setRotation(r):
    M5.Lcd.setRotation(r)

def setBrightness(brightness):
    M5.Lcd.setBrightness(brightness)


def restart_draw(func):
    def wrapper(self, *args, **kwargs):
        self.erase_helper()
        result = func(self, *args, **kwargs)
        self.draw_helper()
        return result
    return wrapper


class FONTS:
    DejaVu9   = M5.m5gfxpy.DejaVu9   
    DejaVu12  = M5.m5gfxpy.DejaVu12  
    DejaVu18  = M5.m5gfxpy.DejaVu18  
    DejaVu24  = M5.m5gfxpy.DejaVu24  
    DejaVu40  = M5.m5gfxpy.DejaVu40  
    DejaVu56  = M5.m5gfxpy.DejaVu56  
    DejaVu72  = M5.m5gfxpy.DejaVu72  
    EFontCN14 = M5.m5gfxpy.efontCN_14
    EFontCN24 = M5.m5gfxpy.efontCN_24
    EFontJA14 = M5.m5gfxpy.efontJA_14
    EFontJA24 = M5.m5gfxpy.efontJA_24
    EFontKR14 = M5.m5gfxpy.efontKR_14
    EFontKR24 = M5.m5gfxpy.efontKR_24



class Label:
    LEFT_ALIGNED = 0
    CENTER_ALIGNED = 1 
    RIGHT_ALIGNED = 2
    def __init__(self, text, x, y, text_sz, text_c, bg_c, font, w=None, font_align=LEFT_ALIGNED):
        self._text = text
        self._x = x
        self._y = y
        self._text_sz = text_sz
        self._text_c = text_c
        self._bg_c = bg_c
        self._font = font
        self._width = w
        self._align = font_align    # TODO:
        self.draw_helper()

    def draw_helper(self):
        stash_style = M5.Lcd.getTextStyle()
        M5.Lcd.setTextColor(self._text_c, self._bg_c)
        M5.Lcd.setTextSize(self._text_sz)

        text_width = M5.Lcd.textWidth(self._text, self._font)
        if self._width is not None:
            if self._align == self.CENTER_ALIGNED:
                x = self._x + (self._width - text_width) // 2
            elif self._align == self.RIGHT_ALIGNED:
                x = self._x + self._width - text_width
            else:
                x = self._x
        else:
            x = self._x
            
        M5.Lcd.drawString(self._text, x, self._y, self._font)
        M5.Lcd.setTextStyle(stash_style)
    def erase_helper(self):
        width = self._width if self._width is not None else M5.Lcd.textWidth(self._text, self._font)
        M5.Lcd.fillRect(self._x, self._y, width, M5.Lcd.fontHeight(self._font))
    
    @restart_draw
    def setText(self, text):
        self._text = text

    @restart_draw
    def setColor(self, text_c, bg_c):
        self._text_c = text_c
        self._bg_c = bg_c
    
    @restart_draw
    def setCursor(self, x, y):
        self._x = x
        self._y = y
    
    @restart_draw
    def setSize(self, text_sz):
        self._text_sz = text_sz

    @restart_draw
    def setFont(self, font):
        self._font = font

    @restart_draw
    def setAlign(self, align):
        self._align = align

    def setVisible(self, visible):
        # self.stash_style = M5.Lcd.getTextStyle()
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()
        # M5.Lcd.setTextStyle(self.stash_style)


class Title:
    def __init__(self, text, text_x, text_c, bg_c, font):
        self._text = text
        self._fg_color = text_c
        self._bg_color = bg_c
        self._font = font
        self._size_w = M5.Lcd.width()
        self._size_h = M5.Lcd.fontHeight(self._font)
        self._text_pos_x0 = text_x
        self.text_pos_y0 = 0
        self._text_size = 1.0
        self.draw_helper()

    def draw_helper(self):
        stash_style = M5.Lcd.getTextStyle()
        self.erase_helper()
        M5.Lcd.setTextColor(self._fg_color, self._bg_color)
        M5.Lcd.setTextSize(self._text_size)
        M5.Lcd.drawString(self._text, self._text_pos_x0, self.text_pos_y0, self._font)
        M5.Lcd.setTextStyle(stash_style)
    def erase_helper(self):
        stash_color = M5.Lcd.getRawColor()
        M5.Lcd.setColor(self._bg_color)
        M5.Lcd.fillRect(0, 0, self._size_w, self._size_h)
        M5.Lcd.setRawColor(stash_color)
    
    @restart_draw
    def setText(self, text):
        self._text = text

    @restart_draw
    def setColor(self, text_c, bg_c):
        self._text_c = text_c

    @restart_draw
    def setSize(self, h):
        self._size_h = h

    @restart_draw
    def setTextCursor(self, text_x):
        self._text_pos_x0 = text_x

    def setVisible(self, visible):
        # self.stash_style = M5.Lcd.getTextStyle()
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()
        # M5.Lcd.setTextStyle(self.stash_style)








class Image:
    def __init__(self, img, x, y, scale_x=1.0, scale_y=1.0):
        self._img_path = img
        self._pos_x0 = x
        self._pos_y0 = y
        self._scale_x = scale_x
        self._scale_y = scale_y
        self._size_w = 0
        self._size_h = 0
        # print(f"Image init with path: {self._img_path}, x: {self._pos_x0}, y: {self._pos_y0}, scale_x: {self._scale_x}, scale_y: {self._scale_y}")
        self.draw_helper()
    
    def draw_helper(self):
        try:
            # print(f"Drawing image from: {self._img_path}")
            M5.Lcd.drawFile(self._img_path, self._pos_x0, self._pos_y0, -1, -1, 0, 0, self._scale_x, self._scale_y)
        except Exception as e:
            print(f"Error drawing image: {e}")
    def erase_helper(self):
        M5.Lcd.fillRect(self._pos_x0, self._pos_y0, self._size_w, self._size_h)
    
    @restart_draw
    def setImage(self, img):
        self._img_path = img
    
    @restart_draw
    def setPosition(self, x, y):
        self._pos_x0 = x
        self._pos_y0 = y
    
    @restart_draw
    def setScale(self, scale_x, scale_y):
        self._scale_x = scale_x
        self._scale_y = scale_y
    
    @restart_draw
    def setSize(self, w, h):
        self._size_w = w
        self._size_h = h
    
    def setVisible(self, visible):
        # self.stash_style = M5.Lcd.getTextStyle()
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()
        # M5.Lcd.setTextStyle(self.stash_style)


class Line:
    def __init__(self, x0, y0, x1, y1, color):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
        self._color = color
        self.draw_helper()
    def draw_helper(self):
        stash_color = M5.Lcd.getRawColor()
        M5.Lcd.setColor(self._color)
        M5.Lcd.drawLine(self._x0, self._y0, self._x1, self._y1)
        M5.Lcd.setRawColor(stash_color)
    def erase_helper(self):
        M5.Lcd.drawLine(self._x0, self._y0, self._x1, self._y1)
    
    @restart_draw
    def setColor(self, color):
        self._color = color
    
    @restart_draw
    def setPoints(self, x0, y0, x1, y1):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
    
    def setVisible(self, visible):
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()

class Circle:
    def __init__(self, x, y, r, color, fill_c):
        self._x = x
        self._y = y
        self._r = r
        self._color = color
        self._fill_c = fill_c
        self.draw_helper()
    def draw_helper(self):
        stash_color = M5.Lcd.getRawColor()
        M5.Lcd.setColor(self._fill_c)
        M5.Lcd.fillCircle(self._x, self._y, self._r)
        M5.Lcd.setColor(self._color)
        M5.Lcd.drawCircle(self._x, self._y, self._r)
        M5.Lcd.setRawColor(stash_color)
    def erase_helper(self):
        M5.Lcd.fillCircle(self._x, self._y, self._r)

    @restart_draw
    def setRadius(self, r):
        self._r = r

    @restart_draw
    def setCursor(self, x, y):
        self._x = x
        self._y = y
    
    @restart_draw
    def setColor(self, color, fill_c):
        self._color = color
        self._fill_c = fill_c
    
    def setVisible(self, visible):
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()





class Rectangle:
    def __init__(self, x, y, w, h, color, fill_c):
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._color = color
        self._fill_c = fill_c
        self.draw_helper()
    def draw_helper(self):
        stash_color = M5.Lcd.getRawColor()
        M5.Lcd.setColor(self._fill_c)
        M5.Lcd.fillRect(self._x, self._y, self._w, self._h)
        M5.Lcd.setColor(self._color)
        M5.Lcd.drawRect(self._x, self._y, self._w, self._h)
        M5.Lcd.setRawColor(stash_color)
    def erase_helper(self):
        M5.Lcd.fillRect(self._x, self._y, self._w, self._h)
    
    @restart_draw
    def setSize(self, w, h):
        self._w = w
        self._h = h

    @restart_draw
    def setColor(self, color, fill_c):
        self._color = color
        self._fill_c = fill_c
    
    @restart_draw
    def setCursor(self, x, y):
        self._x = x
        self._y = y

    def setVisible(self, visible):
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()



class Button:
    def __init__(self, event=None, x=0, y=0, w=0, h=0, color=0, fill_c=0):
        self._event = event
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._color = color
        self._fill_c = fill_c
        self.draw_helper()
    def draw_helper(self):
        M5.Lcd.drawRect(self._x, self._y, self._w, self._h)
        M5.Lcd.setColor(self._color)
        M5.Lcd.fillRect(self._x, self._y, self._w, self._h)
    def erase_helper(self):
        M5.Lcd.fillRect(self._x, self._y, self._w, self._h)

    @restart_draw
    def setColor(self, color, fill_c):
        self._color = color
        self._fill_c = fill_c
    
    @restart_draw
    def setEvent(self, event):
        self._event = event
    
    @restart_draw
    def setPosition(self, x, y):
        self._x = x
        self._y = y
    
    @restart_draw
    def setSize(self, w, h):
        self._w = w
        self._h = h


class Triangle:
    def __init__(self, x0, y0, x1, y1, x2, y2, color, fill_c):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._color = color
        self._fill_c = fill_c
        self.draw_helper()
    def draw_helper(self):
        stash_color = M5.Lcd.getRawColor()
        M5.Lcd.setColor(self._fill_c)
        M5.Lcd.fillTriangle(self._x0, self._y0, self._x1, self._y1, self._x2, self._y2)
        M5.Lcd.setColor(self._color)
        M5.Lcd.drawTriangle(self._x0, self._y0, self._x1, self._y1, self._x2, self._y2)
        M5.Lcd.setRawColor(stash_color)
    def erase_helper(self):
        M5.Lcd.fillTriangle(self._x0, self._y0, self._x1, self._y1, self._x2, self._y2)
    
    @restart_draw
    def setColor(self, color, fill_c):
        self._color = color
        self._fill_c = fill_c
    
    @restart_draw
    def setPoints(self, x0, y0, x1, y1, x2, y2):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    def setVisible(self, visible):
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()






class Qrcode:
    def __init__(self, text, x, y, w, version):
        self._text = text
        self._x = x
        self._y = y
        self._w = w
        self._version = version
        self.draw_helper()
    def draw_helper(self):
        stash_color = M5.Lcd.getRawColor()
        M5.Lcd.setColor(self._color)
        M5.Lcd.qrcode(self._text, self._x, self._y, self._w, self._version)
        M5.Lcd.setRawColor(stash_color)
    def erase_helper(self):
        M5.Lcd.fillRect(self._x, self._y, self._w, self._w)
    
    @restart_draw
    def setText(self, text):
        self._text = text

    @restart_draw
    def setSize(self, w):
        self._w = w
    
    @restart_draw
    def setVersion(self, version):
        self._version = version
    
    @restart_draw
    def setCursor(self, x, y):
        self._x = x
        self._y = y

    def setVisible(self, visible):
        if visible:
            self.draw_helper()
        else:
            self.erase_helper()











































































