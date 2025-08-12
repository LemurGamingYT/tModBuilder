from tkinter.messagebox import showerror, ERROR
from pathlib import Path
from sys import argv

from project_manager import ProjectManager
from ctk_ext import CTkRoot
from project import Project
from editor import Editor


def main():
    root = CTkRoot()

    if len(argv) == 1:
        pm = ProjectManager(root)
        root.switch_to_page(pm)
    else:
        file_path = Path(argv[1])
        if not file_path.exists():
            showerror('Error', 'File does not exist.', icon=ERROR)
            return
        elif not file_path.suffix == '.tmb':
            showerror('Error', 'File is not a valid tModBuilder project file (.tmb).', icon=ERROR)
            return
        
        editor = Editor(root, Project.load(file_path))
        root.switch_to_page(editor)

    root.mainloop()

    if len(argv) == 0:
        pm.save_projects()

if __name__ == '__main__':
    main()
