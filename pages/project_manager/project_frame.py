from tkinter import LEFT, RIGHT

from customtkinter import CTkFrame, CTkLabel, CTkButton

from pages.editor import Editor
from ctk_ext import CTkRoot
from project import Project


class ProjectFrame(CTkFrame):
    # pass in each UI element we need because '.master' is not trustworthy when using customtkinter
    def __init__(self, parent, page, root: CTkRoot, project: Project):
        super().__init__(parent, fg_color='#073B00', height=100, corner_radius=10)

        self.project_manager = page
        self.project = project
        self.parent = parent
        self.root = root

        name_label = CTkLabel(self, text=project.name, font=('Andy', 25, 'bold'))
        name_label.pack(side=LEFT, padx=10)

        path_label = CTkLabel(self, text=project.path, font=('Andy', 20))
        path_label.pack(side=LEFT, padx=10)

        action_buttons = CTkFrame(self, fg_color='transparent')
        action_buttons.pack(side=RIGHT, padx=10)

        CTkButton(
            action_buttons, text='Edit', font=('Andy', 20), fg_color='#094E00',
            hover_color='#0B5C00', corner_radius=10, command=self.edit
        ).pack(pady=5)

        CTkButton(action_buttons, text='Remove', font=('Andy', 20), fg_color='#094E00',
            hover_color='#0B5C00', corner_radius=10, command=self.delete
        ).pack(pady=5)
    
    def edit(self):
        self.project_manager.destroy()

        self.root.switch_to_page(Editor(self.root, self.project))

    def delete(self):
        try:
            idx = self.project_manager.projects.index(self.project)
        except ValueError:
            return
        
        self.project_manager.projects.pop(idx)
        self.project_manager.save_projects()
        self.project_manager.add_projects()
        self.destroy()
