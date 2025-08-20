from tkinter.filedialog import askopenfilename
from abc import ABC, abstractmethod
from dataclasses import dataclass
from tkinter import X, BOTH
from typing import Any
from os import getcwd

from PIL.Image import open as imopen
from customtkinter import (
    CTkFrame, CTkEntry, CTkImage, CTkLabel, CTkButton, CTkCheckBox, CTkToplevel, CTkScrollableFrame
)

from editor_types.rarities import rarities, rarity_colors


class DataType(ABC):
    @abstractmethod
    def display(self, parent: CTkFrame) -> list[Any] | Any:
        """Change what will show up in the properties window in the editor.
Note that this method's return value is NOT added to the parent, it has to be done manually.
There are utility methods in this class to help e.g. `display_entry` and `display_dropdown` which
add to the parent automatically. This method should return what you need in `.read`."""
    
    @abstractmethod
    def read(self, widget) -> 'DataType':
        """Read the value of this data type, the type of widget will be the same as the result of the
`.display` method. This is used for saving the value of the data type."""


    def display_entry(self, parent, value: Any, label_text: str | None = None):
        """Utility method to display an editable entry widget with the given value and label text.
Used by `Int.display`, `Float.display` and `String.display`."""

        if label_text is not None:
            label = CTkLabel(parent, text=label_text, font=('Andy', 20), fg_color='transparent')
            label.pack(fill=X)
        
        entry = CTkEntry(parent, fg_color='#073B00', border_color='#0B5C00', font=('Andy', 20))
        entry.insert(0, value)
        entry.pack(fill=X)
        return entry
    
    def picker_window(self, parent, title: str, choices: list[str]):
        window = CTkToplevel(parent)
        window.title(title)
        window.geometry('400x300')
        picked = ''
        def set_picked(choice: str):
            nonlocal picked
            picked = choice
            window.destroy()

        list_frame = CTkScrollableFrame(
            window, fg_color='#063000', scrollbar_button_color='#095000',
            scrollbar_button_hover_color='#0B5C00', border_color='#0C6500',
            label_text='Select', label_font=('Andy', 20, 'bold'), label_anchor='n'
        )

        for choice in choices:
            CTkButton(
                list_frame, text=choice, fg_color='#073B00', border_color='#0B5C00',
                hover_color='#0C6500', font=('Andy', 20), command=lambda c=choice: set_picked(c)
            ).pack(fill=X, padx=5, pady=5)
        
        list_frame.pack(fill=BOTH, expand=True)
        window.grab_set()
        window.wait_window()
        return picked


@dataclass
class Int(DataType):
    value: int = 0

    def __str__(self):
        return str(self.value)

    def display(self, parent):
        return self.display_entry(parent, self.value)
    
    def read(self, widget):
        return Int(int(widget.get().strip()))

@dataclass
class Float(DataType):
    value: float = 0.0

    def __str__(self):
        return f'{self.value}f'

    def display(self, parent):
        return self.display_entry(parent, self.value)
    
    def read(self, widget):
        return Float(float(widget.get().strip()))

@dataclass
class String(DataType):
    value: str = ''

    def __str__(self):
        return self.value

    def display(self, parent):
        return self.display_entry(parent, self.value)
    
    def read(self, widget):
        return String(widget.get())

@dataclass
class Bool(DataType):
    value: bool = False

    def __str__(self):
        return str(self.value).lower()

    def display(self, parent):
        def check():
            self.value = not self.value
            checkbox.configure(text='true' if self.value else 'false')

        checkbox = CTkCheckBox(
            parent, text='true' if self.value else 'false', fg_color='#095000',
            border_color='#0B5C00', hover_color='#0C6500', checkmark_color='#1EFF00',
            font=('Andy', 20), command=check
        )
        checkbox.pack(fill=X)
        if self.value:
            checkbox.select()
        else:
            checkbox.deselect()
        
        return checkbox
    
    def read(self, widget):
        return Bool(bool(widget.get()))

@dataclass
class Image(DataType):
    path: str = f'{getcwd()}/assets/placeholder_image.png'

    def __post_init__(self):
        self.image = imopen(self.path)
    
    def __str__(self):
        return self.path

    def display(self, parent):
        def browse():
            path = askopenfilename(filetypes=[
                ('Image Files', '*.png'), ('All Files', '*.*')
            ], title='Browse Image')
            if path:
                self.path = path
                self.image = imopen(path)
                img_label.path = self.path
                img_label.configure(image=CTkImage(self.image, size=self.image.size))

        img_label = CTkLabel(parent, image=CTkImage(
            self.image, size=self.image.size
        ), text='')
        img_label.path = self.path
        img_label.pack(fill=X, padx=5)

        browse_btn = CTkButton(
            parent, fg_color='#084400', hover_color='#0B5C00', text='Browse', command=browse,
            font=('Andy', 20)
        )
        browse_btn.pack(fill=X, padx=25, pady=5)
        return img_label

    def read(self, widget):
        path = widget.path
        return Image(path)

@dataclass
class Rarity(DataType):
    rare: str = 'White'

    @property
    def color(self):
        return rarity_colors[self.rare]

    def __post_init__(self):
        self.MIN_RAINBOW_INDEX = 2
        self.rainbow_index = self.MIN_RAINBOW_INDEX
        self.RAINBOW_SPEED_MILLISECONDS = 250

    def __str__(self):
        return f'ItemRarityID.{self.rare.replace(" ", "")}'

    def display(self, parent):
        def rainbow_btn():
            if self.rainbow_index >= len(rarity_colors):
                self.rainbow_index = self.MIN_RAINBOW_INDEX

            rainbow_color = rarity_colors[list(rarity_colors.keys())[self.rainbow_index]]
            btn.configure(fg_color=rainbow_color, text=self.rare)
            self.rainbow_index += 1

            if self.rare not in ('Expert', 'Master'):
                update_button()

            btn.after(self.RAINBOW_SPEED_MILLISECONDS, rainbow_btn)

        def update_button():
            if self.rare in ('Expert', 'Master'):
                rainbow_btn()
            else:
                btn.configure(fg_color=self.color, text=self.rare)

        def window():
            choice = self.picker_window(btn, 'Rarities', rarities)
            if choice != '':
                self.rare = choice
                update_button()

        btn = CTkButton(parent, font=('Andy', 20), corner_radius=10, command=window)
        btn.pack(fill=X, padx=5)
        update_button()
        return btn
    
    def read(self, widget):
        return Rarity(widget.cget('text'))

@dataclass
class CoinValue(DataType):
    platinum: int = 0
    gold: int = 0
    silver: int = 0
    copper: int = 0

    def __str__(self):
        return f'Item.buyPrice({self.platinum}, {self.gold}, {self.silver}, {self.copper})'

    def display(self, parent):
        platinum = self.display_entry(parent, self.platinum, 'Platinum:')
        gold = self.display_entry(parent, self.gold, 'Gold:')
        silver = self.display_entry(parent, self.silver, 'Silver:')
        copper = self.display_entry(parent, self.copper, 'Copper:')
        return [platinum, gold, silver, copper]
    
    def read(self, widget):
        platinum, gold, silver, copper = widget
        return CoinValue(platinum.get(), gold.get(), silver.get(), copper.get())

DATA_TYPES = [Int, Float, String, Bool, Image, Rarity, CoinValue]
