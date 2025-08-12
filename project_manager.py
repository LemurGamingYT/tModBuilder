from tkinter import TOP, BOTTOM, LEFT, RIGHT, X, BOTH, CENTER
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from tkinter import StringVar
from json import loads, dumps
from pathlib import Path

from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkScrollableFrame, CTkToplevel

from ctk_ext import CTkRoot, CTkPage
from project import Project
from editor import Editor


projects_file = Path('projects.json')

class NewProject(CTkToplevel):
    def __init__(self, name: StringVar, path: StringVar):
        super().__init__()

        self.title('New Project')
        self.geometry('400x300')

        self.name_var = name
        self.path_var = path

        self.main_frame = CTkFrame(self, fg_color='#084300')
        self.main_frame.pack(fill=BOTH, expand=True)

        self.name_frame = CTkFrame(self.main_frame, fg_color='transparent')
        self.name_frame.pack(fill=BOTH, expand=True, pady=5)

        self.name_label = CTkLabel(self.name_frame, text='Name:', font=('Andy', 15, 'bold'))
        self.name_label.pack(fill=X)

        self.name_entry = CTkEntry(self.name_frame, textvariable=name, width=200, font=('Andy', 15),
                                   fg_color='#073B00', border_color='#0B5C00')
        self.name_entry.pack(fill=X)

        self.path_frame = CTkFrame(self.main_frame, fg_color='transparent')
        self.path_frame.pack(fill=BOTH, expand=True, pady=5)

        self.path_label = CTkLabel(self.path_frame, text='Path:', font=('Andy', 15, 'bold'))
        self.path_label.pack(fill=X)

        self.path_entry = CTkEntry(self.path_frame, textvariable=path, width=200, font=('Andy', 15),
                                   fg_color='#073B00', border_color='#0B5C00')
        self.path_entry.pack(side=LEFT)

        self.browse_path = CTkButton(self.path_frame, text='Browse', font=('Andy', 15),
                                     fg_color='#073B00', hover_color='#0B5C00',
                                     command=self.browse)
        self.browse_path.pack(side=RIGHT, fill=X)

        self.create = CTkButton(self.main_frame, text='Create', font=('Andy', 20),
                                fg_color='#073B00', hover_color='#0B5C00',
                                command=self.destroy)
        self.create.pack(pady=5)
    
    def browse(self):
        path = askdirectory(mustexist=True, parent=self, title='Browse')
        if path == '':
            return
        
        self.path_var.set(path)

class ProjectFrame(CTkFrame):
    # pass in each UI element we need because '.master' is not trustworthy
    def __init__(self, parent, page: 'ProjectManager', root: CTkRoot, project: Project):
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

class ProjectManager(CTkPage):
    def __init__(self, root: CTkRoot):
        super().__init__(root, fg_color='transparent')

        self.root = root

        root.title('TModBuilder - Project Manager')
        root.geometry('800x600')

        self.top_bar = CTkFrame(self, fg_color='#084300', height=50)
        self.top_bar.pack(side=TOP, fill=X)

        CTkLabel(
            self.top_bar, text='TModBuilder - Project Manager', font=('Andy', 25, 'bold')
        ).pack(anchor=CENTER, padx=10)

        self.project_list = CTkScrollableFrame(self, fg_color='#063000')
        self.project_list.pack(side=BOTTOM, fill=BOTH, expand=True)

        self.projects: list[Project] = []
        self.load_projects()
        self.add_projects()
    
    def new_project(self):
        name_var = StringVar(self)
        path_var = StringVar(self)

        toplevel = NewProject(name_var, path_var)
        toplevel.grab_set()
        toplevel.wait_window()

        name = name_var.get()
        path = Path(path_var.get())
        if not path.exists():
            showerror('Error', 'Path does not exist.')
            return
        
        project = Project(name, path)
        project.save()

        self.projects.append(project)
        self.save_projects()
        self.add_projects()
    
    def add_project(self, project: Project):
        frame = ProjectFrame(self.project_list, self, self.root, project)
        frame.pack(fill=X, padx=10, pady=10)
    
    def add_projects(self):
        for child in self.project_list.winfo_children():
            child.destroy()

        for project in self.projects:
            self.add_project(project)
        
        new_project_button = CTkButton(self.project_list, text='New', font=('Andy', 30),
                                       fg_color='#073B00', hover_color='#0B5C00',
                                       corner_radius=10, command=self.new_project)
        new_project_button.pack(pady=10)
    
    def load_projects(self):
        if projects_file.exists():
            self.projects.clear()
            project_list = loads(projects_file.read_text('utf-8'))
            project_paths = [Path(path) for path in project_list]
            for path in project_paths:
                if not path.exists():
                    showerror('Error', f'Path does not exist: {path.as_posix()}')
                    continue

                self.projects.append(Project.load(path))
    
    def save_projects(self):
        project_paths = [project.file.as_posix() for project in self.projects]
        projects_file.write_text(dumps(project_paths)) # save projects
