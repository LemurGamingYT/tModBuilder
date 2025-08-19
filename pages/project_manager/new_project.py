from tkinter.filedialog import askdirectory
from tkinter import LEFT, RIGHT, X, BOTH
from tkinter import StringVar

from customtkinter import CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkToplevel


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
