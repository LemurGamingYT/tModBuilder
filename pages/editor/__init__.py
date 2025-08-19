from tkinter.messagebox import showerror, showinfo, INFO, ERROR
from tkinter import TOP, LEFT, RIGHT, X, Y, BOTH

from customtkinter import CTkFrame, CTkButton, CTkLabel

from pages.editor.properties import PropertiesFrame
from editor_types.content_types import ContentType
from pages.editor.content_bar import ContentBar
from pages.editor.builder import build_project
from ctk_ext import CTkRoot, CTkPage
from project import Project


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
        showinfo('Saved', f'Your mod has been saved to {self.project.file.as_posix()}', icon=INFO)
    
    def build(self):
        success = build_project(self.project)
        if not success:
            showerror('Error', 'Your mod could not be built.', icon=ERROR)
        else:
            showinfo(
                'Built', f'Your mod has been built to {(self.project.path / "build").as_posix()}',
                icon=INFO
            )
