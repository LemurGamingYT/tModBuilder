from tkinter import X

from customtkinter import CTkButton, CTkScrollableFrame

from editor_types.content_types import ContentType
from project import Project


class ContentBarButton(CTkButton):
    def __init__(
        self, page, parent: 'ContentBar', content_idx: int, content_type: ContentType
    ):
        super().__init__(parent, text=content_type.get_name(), font=('Andy', 15), corner_radius=10,
                         fg_color='#084800', hover_color='#0B6000',
                         command=lambda: page.properties_frame.load_content_properties(
                             content_idx, content_type))

class ContentBar(CTkScrollableFrame):
    def __init__(self, page, project: Project):
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
