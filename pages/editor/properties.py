from tkinter.messagebox import showerror, ERROR
from tkinter import BOTH, X, RIGHT, LEFT
from dataclasses import dataclass, fields
from typing import cast

from customtkinter import CTkBaseClass, CTkFrame, CTkButton, CTkLabel, CTkScrollableFrame

from editor_types.content_types import ContentType, CONTENT_TYPES


@dataclass
class PropertyWidgets:
    widgets: list[CTkBaseClass] | CTkBaseClass
    field_name: str

class PropertiesFrame(CTkFrame):
    def __init__(self, page):
        super().__init__(page, fg_color='#073D00')

        self.current_type = cast(ContentType, None)
        self.current_idx = cast(int, None)
        self.current_widgets = []
        self.page = page
    
    @property
    def is_editting(self):
        return self.current_type is not None and self.current_idx is not None
    
    def reset(self):
        self.current_type = None
        self.current_idx = None
        self.current_widgets.clear()

        for child in self.winfo_children():
            child.destroy()
    
    def save(self):
        if not self.is_editting:
            showerror('Error', 'No content selected.', icon=ERROR)
            return

        kwargs = {}
        for property in self.current_widgets:
            value = getattr(self.current_type, property.field_name)
            content_value = value.read(property.widgets)
            kwargs[property.field_name] = content_value
        
        new_content_type = self.current_type.__class__(**kwargs)
        self.page.project.content[self.current_idx] = new_content_type
        self.page.content_bar.load_content()

        self.reset()
    
    def delete(self):
        if not self.is_editting:
            showerror('Error', 'No content selected.', icon=ERROR)
            return

        self.page.project.content.pop(self.current_idx)
        self.page.content_bar.load_content()
        self.reset()
    
    def load_content_properties(self, content_idx: int, content_type: ContentType):
        for child in self.winfo_children():
            child.destroy()
        
        self.current_type = content_type
        self.current_idx = content_idx

        properties = CTkScrollableFrame(
            self, fg_color='transparent', label_anchor='n', label_font=('Andy', 20, 'bold'),
            label_text=content_type.get_name(), label_fg_color='transparent',
            scrollbar_button_color='#095000', scrollbar_button_hover_color='#0B5C00',
        )
        properties.pack(fill=BOTH, expand=True, padx=10, pady=10)

        actions_frame = CTkFrame(properties, fg_color='transparent')
        actions_frame.pack(fill=X, pady=10)

        cancel_button = CTkButton(
            actions_frame, text='Cancel', font=('Andy', 30), width=20, height=30,
            fg_color='#073B00', hover_color='#0B5C00', corner_radius=10, command=self.reset
        )
        cancel_button.pack(side=RIGHT, padx=10)

        save_button = CTkButton(
            actions_frame, text='Save', font=('Andy', 30), width=20, height=30,
            fg_color='#073B00', hover_color='#0B5C00', corner_radius=10, command=self.save
        )
        save_button.pack(side=RIGHT, padx=10)

        delete_button = CTkButton(
            actions_frame, text='Delete', font=('Andy', 30), width=20, height=30,
            fg_color='#073B00', hover_color='#0B5C00', corner_radius=10, command=self.delete
        )
        delete_button.pack(side=RIGHT, padx=10)

        for field in fields(content_type):
            field_frame = CTkFrame(properties, fg_color='transparent')
            field_frame.pack(fill=X, pady=10, padx=10)

            label = CTkLabel(field_frame, text=f'{field.name}:', font=('Andy', 20))
            label.pack(side=LEFT)

            value = getattr(content_type, field.name)
            self.current_widgets.append(PropertyWidgets(value.display(properties), field.name))
    
    def load_content_picker(self):
        if self.is_editting:
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
