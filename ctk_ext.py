from tkinter import BOTH

from customtkinter import CTk, CTkFrame


class CTkPage(CTkFrame):
    pass

class CTkRoot(CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.current_page = None

    def switch_to_page(self, page: CTkPage):
        self.current_page = page
        page.pack(fill=BOTH, expand=True)
