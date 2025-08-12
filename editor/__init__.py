from tkinter.messagebox import showerror, showinfo
from tkinter import TOP, LEFT, RIGHT, X, Y, BOTH
from dataclasses import fields
from typing import cast, Any

from customtkinter import CTkBaseClass, CTkFrame, CTkButton, CTkLabel, CTkScrollableFrame

from editor_types.content_types import ContentType, CONTENT_TYPES
from editor.builder import build_project
from ctk_ext import CTkRoot, CTkPage
from project import Project


class ContentBarButton(CTkButton):
    def __init__(
        self, page: 'Editor', parent: 'ContentBar', content_idx: int, content_type: ContentType
    ):
        super().__init__(parent, text=content_type.get_name(), font=('Andy', 15), corner_radius=10,
                         fg_color='#084800', hover_color='#0B6000',
                         command=lambda: page.properties_frame.load_content_properties(
                             content_idx, content_type))

class ContentBar(CTkScrollableFrame):
    def __init__(self, page: 'Editor', project: Project):
        super().__init__(page, fg_color='#063000', label_anchor='n', label_font=('Andy', 20, 'bold'),
                         label_text='Mod Content', label_fg_color='transparent')
        
        self.project = project
        self.page = page

        self.load_content()

    def load_content(self):
        for child in self.winfo_children():
            child.destroy()

        for i, content_type in enumerate(self.project.content):
            btn = ContentBarButton(self.page, self, i, content_type)
            btn.pack(fill=X, padx=10, pady=10)
        
        new_content_button = CTkButton(self, text='New', font=('Andy', 30),
                                       fg_color='#073B00', hover_color='#0B5C00',
                                       corner_radius=10, command=self.pick_content_type)
        new_content_button.pack(pady=10)
    
    def pick_content_type(self):
        self.page.properties_frame.load_content_picker()

class PropertiesFrame(CTkFrame):
    def __init__(self, page: 'Editor'):
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
            showerror('Error', 'No content selected.')
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

class Editor(CTkPage):
    def __init__(self, root: CTkRoot, project: Project):
        super().__init__(root, fg_color='transparent')

        self.project = project
        self.root = root

        root.title('TModBuilder - Editor')
        root.geometry('800x600')

        self.top_bar = CTkFrame(self, fg_color='#084300', height=50)
        self.top_bar.pack(fill=X, side=TOP)

        self.currently_editing = CTkLabel(
            self.top_bar, text=f'Currently editing: {project.name} ({project.path})',
            font=('Andy', 15)
        )
        self.currently_editing.pack(side=LEFT, padx=5)

        self.save_btn = CTkButton(self.top_bar, text='Save', font=('Andy', 20), width=20, height=30,
                                 fg_color='#073B00', hover_color='#0B6000',
                                 corner_radius=10, command=self.save)
        self.save_btn.pack(side=LEFT, padx=5)

        self.build_btn = CTkButton(self.top_bar, text='Build', font=('Andy', 20), width=20, height=30,
                                 fg_color='#073B00', hover_color='#0B6000',
                                 corner_radius=10, command=self.build)
        self.build_btn.pack(side=LEFT, padx=5)

        CTkLabel(self.top_bar, text='TModBuilder - Editor', font=('Andy', 20)).pack(side=RIGHT, padx=5)

        self.content_bar = ContentBar(self, project)
        self.content_bar.pack(fill=Y, side=LEFT)

        self.properties_frame = PropertiesFrame(self)
        self.properties_frame.pack(fill=BOTH, expand=True, side=RIGHT)
    
    def create_content(self, content_type: type[ContentType]):
        content = content_type()
        self.project.content.append(content)
        self.content_bar.load_content()
        self.properties_frame.load_content_properties(len(self.project.content) - 1, content)
    
    def save(self):
        self.project.save()
        showinfo('Saved', f'Your mod has been saved to {self.project.file.as_posix()}')
    
    def build(self):
        build_project(self.project)
        showinfo('Built', f'Your mod has been built to {(self.project.path / "build").as_posix()}')
