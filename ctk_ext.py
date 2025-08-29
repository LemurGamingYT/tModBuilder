from tkinter import BOTH

from customtkinter import CTk, CTkFrame
from overloading import overload


@overload()
def rgb_to_hex(r: int, g: int, b: int):
    return f'#{r:02x}{g:02x}{b:02x}'

@overload(rgb_to_hex)
def rgb_tuple_to_hex(rgb: tuple[int, int, int]):
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

def hex_to_rgb(hex: str):
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

class CTkPage(CTkFrame):
    pass

class CTkRoot(CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.current_page = None

    def switch_to_page(self, page: CTkPage):
        self.current_page = page
        page.pack(fill=BOTH, expand=True)
