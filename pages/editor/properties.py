from tkinter.messagebox import showerror, ERROR
from tkinter import BOTH, X, RIGHT, LEFT
from dataclasses import fields
from typing import cast, Any

from customtkinter import CTkBaseClass, CTkFrame, CTkButton, CTkLabel, CTkScrollableFrame

from editor_types.content_types import ContentType, CONTENT_TYPES


class PropertiesFrame(CTkFrame):
    def __init__(self, page):
        super().__init__(page, fg_color='#073D00')

        self.current_type = cast(ContentType, None)
        self.current_idx = cast(int, None)
        self.page = page
    
    def reset(self):
        self.current_type = None
        self.current_idx = None

        for child in self.winfo_children():
            child.destroy()
    
    def save(self, widgets: list[tuple[list[CTkBaseClass] | CTkBaseClass, str]]):
        if self.current_type is None or self.current_idx is None:
            showerror('Error', 'No content selected.', icon=ERROR)
            return

        kwargs = {}
        for widget, field_name in widgets:
            value = getattr(self.current_type, field_name)
            content_value = value.read(widget)
            kwargs[field_name] = content_value
        
        new_content_type = self.current_type.__class__(**kwargs)
        self.page.project.content[self.current_idx] = new_content_type
        self.page.content_bar.load_content()

        self.reset()
    
    def load_content_properties(self, content_idx: int, content_type: ContentType):
        for child in self.winfo_children():
            child.destroy()
        
        self.current_type = content_type
        self.current_idx = content_idx

        properties = CTkScrollableFrame(self, fg_color='transparent', label_anchor='n',
                                        label_font=('Andy', 20, 'bold'),
                                        label_text=content_type.get_name(),
                                        label_fg_color='transparent')
        properties.pack(fill=BOTH, expand=True, padx=10, pady=10)

        actions_frame = CTkFrame(properties, fg_color='transparent')
        actions_frame.pack(fill=X, pady=10)

        content_widgets: list[tuple[list[Any] | Any, str]] = []

        save_button = CTkButton(
            actions_frame, text='Save', font=('Andy', 30), width=20, height=30,
            fg_color='#073B00', hover_color='#0B5C00',
            corner_radius=10, command=lambda: self.save(content_widgets)
        )
        save_button.pack(side=RIGHT, padx=10)

        for field in fields(content_type):
            field_frame = CTkFrame(properties, fg_color='transparent')
            field_frame.pack(fill=X, pady=10, padx=10)

            label = CTkLabel(field_frame, text=f'{field.name}:', font=('Andy', 20))
            label.pack(side=LEFT)

            value = getattr(content_type, field.name)
            content_widgets.append((value.display(properties), field.name))
    
    def load_content_picker(self):
        if self.current_type is not None and self.current_idx is not None:
            showerror('Error', 'You must save the current content before creating a new one.',
                      icon=ERROR)
            return
        
        all_content_types = CTkScrollableFrame(self, fg_color='#084300', label_anchor='n',
                                               label_font=('Andy', 20, 'bold'),
                                               label_text='Select Content Type',
                                               label_fg_color='transparent')
        all_content_types.pack(fill=BOTH, expand=True, padx=10, pady=10)

        for content_type in CONTENT_TYPES:
            btn = CTkButton(all_content_types, text=content_type.__name__, fg_color='#073B00',
                            font=('Andy', 20), corner_radius=10, hover_color='#0B6000',
                            command=lambda typ=content_type: self.page.create_content(typ))
            btn.pack(padx=10, pady=10)
