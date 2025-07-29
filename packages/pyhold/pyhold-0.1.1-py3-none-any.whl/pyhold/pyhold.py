import xml.etree.ElementTree as ET
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ast



class pyhold:
    def __init__(self, filename="pyhold.xml", mode="keyvalue", auto_sync=True, auto_reload=True):
        self.filename = filename
        self.mode = mode
        self.auto_sync = auto_sync
        self.auto_reload = auto_reload
        if self.auto_reload:
            if not os.path.exists(self.filename):
                if self.mode == "keyvalue":
                    self.volatileMem = []
            else:
                self.volatileMem = []
                self.load_pyhold()
        else:
            self.volatileMem = []

    def write(self, key=None, value=None):
        if self.mode == "keyvalue":
            if key is None:
                raise ValueError("Key must be provided in keyvalue mode.")
            for item in self.volatileMem:
                if item.key == key:
                    item.value = value
                    item.dtype = self.__keyvalNode(key, value).dtype
                    if self.auto_sync:
                        self.save_pyhold()
                    return
            tempNode = self.__keyvalNode(key, value)
            self.volatileMem.append(tempNode)
            if self.auto_sync:
                self.save_pyhold()

    def __getitem__(self, key):
        if self.mode == "keyvalue":
            for item in self.volatileMem:
                if item.key == key:
                    return item.value
            raise KeyError(f"Key '{key}' not found.")
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __len__(self):
        if self.mode == "keyvalue":
            return len(self.volatileMem)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __iter__(self):
        if self.mode == "keyvalue":
            return iter(self.volatileMem)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __contains__(self, key):
        if self.mode == "keyvalue":
            return any(item.key == key for item in self.volatileMem)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def __setitem__(self, key, value):
        if self.mode == "keyvalue":
            for item in self.volatileMem:
                if item.key == key:
                    item.value = value
                    if self.auto_sync:
                        self.save_pyhold()
                    return
            self.write(key, value)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")
    
    def __delitem__(self, key):
        if self.mode == "keyvalue":
            for i, item in enumerate(self.volatileMem):
                if item.key == key:
                    del self.volatileMem[i]
                    if self.auto_sync:
                        self.save_pyhold()
                    return
            raise KeyError(f"Key '{key}' not found.")
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def pop(self, key):
        if self.mode == "keyvalue":
            for i, item in enumerate(self.volatileMem):
                if item.key == key:
                    value = item.value
                    del self.volatileMem[i]
                    if self.auto_sync:
                        self.save_pyhold()
                    return value
            raise KeyError(f"Key '{key}' not found.")
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def save_pyhold(self):
        if self.mode == "keyvalue":
            root = ET.Element("pyhold")
            for item in self.volatileMem:
                key_val = ET.SubElement(root, "keyval")

                key_elem = ET.SubElement(key_val, "key")
                key_elem.text = item.key

                value_elem = ET.SubElement(key_val, "value")
                value_elem.set("dtype", item.dtype)

                if item.dtype in ["dict", "list", "tuple"]:
                    value_elem.text = json.dumps(item.value)
                elif item.value is None:
                    value_elem.text = "None"
                else:
                    value_elem.text = str(item.value)

            tree = ET.ElementTree(root)
            tree.write(self.filename, encoding='utf-8', xml_declaration=True)
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def load_pyhold(self):
        if not os.path.exists(self.filename):
            return

        self.volatileMem.clear()
        tree = ET.parse(self.filename)
        root = tree.getroot()

        for keyval in root.findall("keyval"):
            key = keyval.find("key").text
            value_elem = keyval.find("value")
            dtype = value_elem.attrib.get("dtype", "str")
            value_str = value_elem.text

            if dtype == "int":
                value = int(value_str)
            elif dtype == "float":
                value = float(value_str)
            elif dtype == "bool":
                value = value_str == "True"
            elif dtype == "dict":
                value = json.loads(value_str)
            elif dtype == "list":
                value = json.loads(value_str)
            elif dtype == "tuple":
                value = tuple(json.loads(value_str))
            elif dtype == "NoneType" or value_str == "None":
                value = None
            else:
                value = value_str

            self.volatileMem.append(self.__keyvalNode(key, value))
    
    def get(self, key, default=None):
        if self.mode == "keyvalue":
            for item in self.volatileMem:
                if item.key == key:
                    return item.value
            return default
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")
    
    def keys(self):
        if self.mode == "keyvalue":
            return [item.key for item in self.volatileMem]
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")
    
    def values(self):
        if self.mode == "keyvalue":
            return [item.value for item in self.volatileMem]
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")
    
    def items(self):
        if self.mode == "keyvalue":
            return [(item.key, item.value) for item in self.volatileMem]
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")
    
    def clear(self):
        if self.mode == "keyvalue":
            self.volatileMem.clear()
            if self.auto_sync:
                self.save_pyhold()
        else:
            raise NotImplementedError("Only keyvalue mode is implemented.")

    def showGUI(self):
        if self.mode != "keyvalue":
            raise NotImplementedError("Only keyvalue mode is implemented for GUI.")

        # Main window setup
        self.root = tk.Tk()
        self.root.title(f"pyhold Key-Value Store - {self.filename}")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title and info
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="pyhold Key-Value Store Manager", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        info_label = ttk.Label(title_frame, text=f"File: {self.filename} | Items: {len(self.volatileMem)}")
        info_label.pack(side=tk.RIGHT)
        self.info_label = info_label
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Add/Edit section
        ttk.Label(control_frame, text="Key:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.key_entry = ttk.Entry(control_frame, width=20)
        self.key_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(control_frame, text="Value:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.value_text = tk.Text(control_frame, width=20, height=4, wrap=tk.WORD)
        self.value_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Value type selection
        ttk.Label(control_frame, text="Type:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.type_var = tk.StringVar(value="str")
        type_combo = ttk.Combobox(control_frame, textvariable=self.type_var, 
                                  values=["str", "int", "float", "bool", "list", "dict", "tuple"], 
                                  state="readonly", width=17)
        type_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=6, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="Add/Update", command=self.add_update_item).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_view).pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        ttk.Separator(control_frame, orient='horizontal').grid(row=7, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(control_frame, text="File Operations:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        
        file_btn_frame = ttk.Frame(control_frame)
        file_btn_frame.grid(row=9, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_btn_frame, text="Save", command=self.manual_save).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(file_btn_frame, text="Reload", command=self.manual_reload).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(file_btn_frame, text="Export JSON", command=self.export_json).pack(fill=tk.X, pady=(0, 5))
        
        # Search section
        ttk.Separator(control_frame, orient='horizontal').grid(row=10, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(control_frame, text="Search:", font=('Arial', 10, 'bold')).grid(row=11, column=0, sticky=tk.W, pady=(0, 5))
        
        self.search_entry = ttk.Entry(control_frame, width=20)
        self.search_entry.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.filter_items)
        
        ttk.Button(control_frame, text="Clear Search", command=self.clear_search).grid(row=13, column=0, sticky=(tk.W, tk.E))
        
        # Right panel - Data display
        data_frame = ttk.LabelFrame(main_frame, text="Data Store", padding="10")
        data_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Treeview for better data display
        columns = ('Key', 'Value', 'Type')
        self.tree = ttk.Treeview(data_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.tree.heading('Key', text='Key')
        self.tree.heading('Value', text='Value')
        self.tree.heading('Type', text='Type')
        
        self.tree.column('Key', width=150, minwidth=100)
        self.tree.column('Value', width=300, minwidth=200)
        self.tree.column('Type', width=80, minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind events
        self.tree.bind('<ButtonRelease-1>', self.on_item_select)
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
        # Initial population
        self.refresh_view()
        
        # Start the GUI
        self.root.mainloop()
    
    def add_update_item(self):
        key = self.key_entry.get().strip()
        value_str = self.value_text.get(1.0, tk.END).strip()
        value_type = self.type_var.get()
        
        if not key:
            messagebox.showerror("Error", "Key cannot be empty!")
            return
        
        try:
            # Convert value based on type
            if value_type == "int":
                value = int(value_str)
            elif value_type == "float":
                value = float(value_str)
            elif value_type == "bool":
                value = value_str.lower() in ('true', '1', 'yes', 'on')
            elif value_type in ["list", "dict", "tuple"]:
                value = ast.literal_eval(value_str)
                if value_type == "tuple":
                    value = tuple(value)
            else:  # str
                value = value_str
            
            # Add/update the item
            self[key] = value
            self.refresh_view()
            self.status_label.config(text=f"Added/Updated: {key}")
            
            # Clear inputs
            self.key_entry.delete(0, tk.END)
            self.value_text.delete(1.0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid value for type {value_type}: {str(e)}")
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected!")
            return
        
        item = self.tree.item(selected[0])
        key = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete key '{key}'?"):
            try:
                del self[key]
                self.refresh_view()
                self.status_label.config(text=f"Deleted: {key}")
            except KeyError:
                messagebox.showerror("Error", f"Key '{key}' not found!")
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all data? This cannot be undone!"):
            self.volatileMem.clear()
            if self.auto_sync:
                self.save_pyhold()
            self.refresh_view()
            self.status_label.config(text="All data cleared")
    
    def refresh_view(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add current items
        search_term = self.search_entry.get().lower() if hasattr(self, 'search_entry') else ""
        
        for item in self.volatileMem:
            if not search_term or search_term in item.key.lower() or search_term in str(item.value).lower():
                # Truncate long values for display
                display_value = str(item.value)
                if len(display_value) > 100:
                    display_value = display_value[:97] + "..."
                
                self.tree.insert('', tk.END, values=(item.key, display_value, item.dtype))
        
        # Update info label
        if hasattr(self, 'info_label'):
            self.info_label.config(text=f"File: {self.filename} | Items: {len(self.volatileMem)}")
    
    def on_item_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            key = item['values'][0]
            
            # Find the actual item
            for mem_item in self.volatileMem:
                if mem_item.key == key:
                    self.key_entry.delete(0, tk.END)
                    self.key_entry.insert(0, key)
                    
                    self.value_text.delete(1.0, tk.END)
                    if mem_item.dtype in ["dict", "list", "tuple"]:
                        self.value_text.insert(1.0, json.dumps(mem_item.value, indent=2))
                    else:
                        self.value_text.insert(1.0, str(mem_item.value))
                    
                    self.type_var.set(mem_item.dtype)
                    break
    
    def on_item_double_click(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            key = item['values'][0]
            
            # Find and show full value in popup
            for mem_item in self.volatileMem:
                if mem_item.key == key:
                    popup = tk.Toplevel(self.root)
                    popup.title(f"Value for key: {key}")
                    popup.geometry("600x400")
                    
                    text_widget = tk.Text(popup, wrap=tk.WORD)
                    scrollbar = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=text_widget.yview)
                    text_widget.configure(yscrollcommand=scrollbar.set)
                    
                    if mem_item.dtype in ["dict", "list", "tuple"]:
                        text_widget.insert(1.0, json.dumps(mem_item.value, indent=2))
                    else:
                        text_widget.insert(1.0, str(mem_item.value))
                    
                    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                    break
    
    def filter_items(self, event):
        self.refresh_view()
    
    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_view()
    
    def manual_save(self):
        try:
            self.save_pyhold()
            self.status_label.config(text="Data saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def manual_reload(self):
        try:
            self.load_pyhold()
            self.refresh_view()
            self.status_label.config(text="Data reloaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload: {str(e)}")
    
    def export_json(self):
        try:
            data = {item.key: item.value for item in self.volatileMem}
            json_filename = self.filename.replace('.xml', '.json')
            
            with open(json_filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.status_label.config(text=f"Exported to {json_filename}")
            messagebox.showinfo("Success", f"Data exported to {json_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

    class __keyvalNode:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.dtype = type(value).__name__