from tkinter import TOP, BOTTOM, X, BOTH, CENTER
from tkinter.messagebox import showerror, ERROR
from tkinter import StringVar
from json import loads, dumps
from pathlib import Path

from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkScrollableFrame

from pages.project_manager.project_frame import ProjectFrame
from pages.project_manager.new_project import NewProject
from ctk_ext import CTkRoot, CTkPage
from project import Project


projects_file = Path.cwd() / 'projects.json'

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
        if name == '' or path == '':
            return
        
        if not path.exists():
            showerror('Error', 'Path does not exist.', icon=ERROR)
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
                    showerror('Error', f'Path does not exist: {path.as_posix()}', icon=ERROR)
                    continue

                self.projects.append(Project.load(path))
    
    def save_projects(self):
        project_paths = [project.file.as_posix() for project in self.projects]
        projects_file.write_text(dumps(project_paths)) # save projects
