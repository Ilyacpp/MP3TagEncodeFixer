# this is not work by default on mac os sequoia 15.4.1 
# because they but brouken tkinter, so we need:
# 1 install last python3 version
# 2 in vs_code gui chose this python in right bottom combobox
# 3 in vs_code terminal: python3 -m pip install mutagen

# to make app
# 4 in vs_code terminal: python3 -m pip install pyinstaller
# 5 in vs_code terminal: pyinstaller --onefile --windowed --name MP3TagEncodeFixer  MP3TagEncodeFixer.py
# 6 in script folder you will get dist folder

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from mutagen.id3 import ID3, TextFrame
from encodings.aliases import aliases

class TrackData:
    id3_to_python_encod = {
            0: 'latin1',
            1: 'utf_16',
            2: 'utf_16_be',
            3: 'utf_8'
        }
            
    def __init__(self, filepath):
        self.filepath   = Path(filepath)
        self.tags       = ID3(filepath)
        self._checked    = False
        self.modified   = False
        self.exception  = False

    def set_checked(self, value):
        self._checked = True if value == True and self.exception == False else False

    def get_checked(self):
        return self._checked and not self.exception
    
    def row_values(self, encoding):
        self.exception = False
        before = ""
        after = ""

        for frame_id in self.tags:
            tag = self.tags[frame_id]
            
            if isinstance(tag, TextFrame):
                curr_encoding_str = str(tag.encoding).replace('Encoding.','')
                before += f"{curr_encoding_str} {tag.text} | "
                try:                           
                    after += f"{str(tag.text).encode(self.id3_to_python_encod[tag.encoding]).decode(encoding)} | "
                except Exception as e:
                    after += "encode exception |"
                    self.exception = True
        return (
            '☑' if self.get_checked() else '☐',
            self.filepath.name,
            before,
            after
        )
    


    

class MP3TagEditor:
    def __init__(self, root):
        self.root = root
        self.tracks = []
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Control Panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)
        
        self.btn_folder = ttk.Button(
            control_frame, 
            text="Select Folder",
            command=self.load_folder
        )
        self.btn_folder.pack(side='left', padx=5)

        ttk.Label(
            control_frame, 
            text="From:"
        ).pack(side='left', padx=0)

        self.cmb_encod_from = ttk.Combobox(
            control_frame, 
            values=self.get_all_encodings(),
            state='readonly',
            width=10
        )
        self.cmb_encod_from.set('cp1251')
        self.cmb_encod_from.bind("<<ComboboxSelected>>", self.on_cmb_encodings_select)
        self.cmb_encod_from.pack(side='left', padx=5)

        ttk.Label(
            control_frame, 
            text="To:"
        ).pack(side='left', padx=0)

        self.cmb_encod_to = ttk.Combobox(
            control_frame, 
            values=['LATIN1', 'UTF16','UTF16BE', 'UTF8'],
            state='readonly',
            width=10
        )
        self.cmb_encod_to.set('UTF8')
        self.cmb_encod_to.pack(side='left', padx=5)
        
        self.btn_apply = ttk.Button(
            control_frame,
            text="Apply",
            command=self.apply_changes
        )       
        self.btn_apply.pack(side='left', padx=5)
        
        # Table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill='both', expand=True, pady=5)

        self.tree = ttk.Treeview(
            table_frame,
            columns=('check', 'file', 'before_change', 'after_change'),
            show='headings',
            selectmode='browse'
        )
        
        self.tree.heading('check',          text='☐')
        self.tree.column('check',           width=20,  stretch=False)
        
        self.tree.heading('file',           text='File')
        self.tree.column('file',            width=245, stretch=False)
        
        self.tree.heading('before_change',  text='Before')
        self.tree.column('before_change',   width=250, stretch=False)
        
        self.tree.heading('after_change',   text='After')
        self.tree.column('after_change',    width=250, stretch=False)
        
        # Scroll
        vscrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        vscrollbar.pack(side="right", fill="y")
        hscrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        hscrollbar.pack(side="bottom", fill="x")

        
        self.tree.pack(side='left', fill='both', expand=True)

        self.tree.configure(
                                yscrollcommand=vscrollbar.set,
                                xscrollcommand=hscrollbar.set
                            )
        
        # Table on click
        self.tree.bind('<Button-1>', self.on_tree_click)
        
    def load_folder(self):
        folder = filedialog.askdirectory(title="Choose folder with MP3")
        if not folder:
            return
            
        self.tracks = []
        for f in Path(folder).glob('*.mp3'):
            try:
                self.tracks.append(TrackData(f))
            except Exception as e:
                print(f"load error {f}: {e}")
        
        self.select_all(True)
    
    def update_table(self, index=None):
        if index is not None:
            track = self.tracks[index]
            item = self.tree.get_children()[index]
            self.tree.item(item, values=track.row_values(str(self.cmb_encod_from.get())))
        else:
            self.tree.delete(*self.tree.get_children())
            for track in self.tracks:
                self.tree.insert('', 'end', values=track.row_values(str(self.cmb_encod_from.get())))

    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        if column != '#1': return

        if region == 'cell':          
            self.tree.heading("check", text = '☐') 
            item = self.tree.identify_row(event.y)           
            index = self.tree.index(item)
            self.tracks[index].set_checked(not self.tracks[index].get_checked())
            self.update_table(index)  

        elif region == 'heading':
            col_text = self.tree.heading(column,'text')      
            self.select_all(True if col_text == '☐' else False) 

    def select_all(self, select):
        self.tree.heading("check", text = '☑' if select == True else '☐')
        for track in self.tracks:
            track.set_checked(select)
        self.update_table() 

    def on_cmb_encodings_select(self, event):
        self.update_table()    

    def get_all_encodings(self):
        return sorted(set(aliases.values()))
    
    def apply_changes(self):
        for track in self.tracks:
            if track.get_checked():
                try:
                    from_encoding = self.cmb_encod_from.get()  
                    to_encoding_index = self.cmb_encod_to.current()

                    for frame_id in track.tags:
                        tag = track.tags[frame_id]
                        if isinstance(tag, TextFrame):
                            original_text = tag.text.copy()
                            
                            try:
                             
                                converted_text = [
                                    text.encode(track.id3_to_python_encod[tag.encoding]).decode(from_encoding)
                                    for text in original_text
                                ]
                                
                                tag.text = converted_text
                                tag.encoding = to_encoding_index  # it convert by himself
                                
                            except Exception as e:
                                print(f"convert error: {str(e)}")
                                       
                    track.tags.save()
                           
                except Exception as e:
                    print(f"save error: {str(e)}")
        
        self.update_table()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("MP3TagEncodeFixer")
    root.geometry("800x600")
    
    app = MP3TagEditor(root)
    root.mainloop()