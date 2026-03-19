import customtkinter as ctk
import keyboard
import pyperclip
import pyautogui
import json
import os
import time
import threading
import uuid

PROMPTS_FILE = "prompts.json"

BG_COLOR = "#12121A"
FG_COLOR = "#F2F2F2"
CARD_COLOR = "#1B1B26"
PRIMARY_COLOR = "#7C52FF"
BORDER_COLOR = "#3B3B4A"

class EditDialog(ctk.CTkToplevel):
    def __init__(self, parent, prompt_data=None, on_save=None):
        super().__init__(parent)
        self.title("Editar Prompt" if prompt_data else "Nuevo Prompt")
        self.geometry("400x450")
        
        # Make the dialog modal and always on top of the parent
        self.transient(parent)
        self.attributes("-topmost", True)
        
        self.configure(fg_color=BG_COLOR)
        
        # Center the dialog relative to parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (400 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (450 // 2)
        self.geometry(f"+{x}+{y}")
        
        self.prompt_data = prompt_data or {"id": str(uuid.uuid4()), "title": "", "text": "", "category": "General", "archived": False}
        self.on_save = on_save
        
        # Form
        ctk.CTkLabel(self, text="Título:", text_color=FG_COLOR).pack(anchor="w", padx=20, pady=(20, 0))
        self.title_entry = ctk.CTkEntry(self, fg_color=CARD_COLOR, border_color=BORDER_COLOR, text_color=FG_COLOR)
        self.title_entry.pack(fill="x", padx=20, pady=5)
        self.title_entry.insert(0, self.prompt_data.get("title", ""))
        
        ctk.CTkLabel(self, text="Categoría:", text_color=FG_COLOR).pack(anchor="w", padx=20, pady=(10, 0))
        self.category_entry = ctk.CTkEntry(self, fg_color=CARD_COLOR, border_color=BORDER_COLOR, text_color=FG_COLOR)
        self.category_entry.pack(fill="x", padx=20, pady=5)
        self.category_entry.insert(0, self.prompt_data.get("category", "General"))
        
        ctk.CTkLabel(self, text="Texto del Prompt:", text_color=FG_COLOR).pack(anchor="w", padx=20, pady=(10, 0))
        self.text_box = ctk.CTkTextbox(self, fg_color=CARD_COLOR, border_color=BORDER_COLOR, text_color=FG_COLOR, height=120)
        self.text_box.pack(fill="x", padx=20, pady=5)
        self.text_box.insert("0.0", self.prompt_data.get("text", ""))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="transparent", border_width=1, border_color=BORDER_COLOR, hover_color=BORDER_COLOR, command=self.destroy).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Guardar", fg_color=PRIMARY_COLOR, hover_color="#6342cc", command=self.save).pack(side="right", expand=True, padx=5)
        
        # Focus this window and grab events so it doesn't go behind the main app
        self.focus_force()
        self.grab_set()

    def save(self):
        self.prompt_data["title"] = self.title_entry.get().strip()
        self.prompt_data["category"] = self.category_entry.get().strip() or "General"
        self.prompt_data["text"] = self.text_box.get("0.0", "end").strip()
        if self.on_save:
            self.on_save(self.prompt_data)
        self.destroy()

class PromptItem(ctk.CTkFrame):
    def __init__(self, master, prompt_data, command_execute, command_edit, command_delete, command_archive, **kwargs):
        super().__init__(master, fg_color=CARD_COLOR, border_color=BORDER_COLOR, border_width=1, corner_radius=8, **kwargs)
        self.prompt_data = prompt_data
        
        self.columnconfigure(0, weight=1)
        
        # Title that can be clicked to execute
        self.title_btn = ctk.CTkButton(
            self, text=prompt_data.get("title", ""), font=("Inter", 14), 
            fg_color="transparent", hover_color=PRIMARY_COLOR, text_color=FG_COLOR, anchor="w",
            command=lambda: command_execute(self.prompt_data.get("text", ""))
        )
        self.title_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 3 dot menu button
        self.menu_btn = ctk.CTkButton(
            self, text="⋮", font=("Inter", 18, "bold"), width=30,
            fg_color="transparent", hover_color=BORDER_COLOR, text_color=FG_COLOR,
            command=self.toggle_menu
        )
        self.menu_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Menu frame (hidden by default)
        self.menu_frame = ctk.CTkFrame(self, fg_color=BORDER_COLOR, corner_radius=6)
        
        is_archived = prompt_data.get("archived", False)
        archive_icon = "⤴️ Desarchivar" if is_archived else "📦 Archivar"
        
        self.edit_btn = ctk.CTkButton(self.menu_frame, text="✏️ Editar", width=100, height=24, fg_color="transparent", hover_color=CARD_COLOR, command=lambda: [self.toggle_menu(), command_edit(self.prompt_data)])
        self.archive_btn = ctk.CTkButton(self.menu_frame, text=archive_icon, width=100, height=24, fg_color="transparent", hover_color=CARD_COLOR, command=lambda: [self.toggle_menu(), command_archive(self.prompt_data)])
        self.delete_btn = ctk.CTkButton(self.menu_frame, text="🗑️ Borrar", width=100, height=24, fg_color="transparent", hover_color="#cc4242", text_color="white", command=lambda: [self.toggle_menu(), command_delete(self.prompt_data)])
        
        self.edit_btn.pack(fill="x", pady=1, padx=1)
        self.archive_btn.pack(fill="x", pady=1, padx=1)
        self.delete_btn.pack(fill="x", pady=1, padx=1)
        
        self.menu_visible = False

    def toggle_menu(self):
        if self.menu_visible:
            self.menu_frame.grid_forget()
            self.menu_visible = False
        else:
            self.menu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(0,5))
            self.menu_visible = True

class PromperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Promper")
        self.geometry("600x550")
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.attributes('-alpha', 0.0)
        
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        
        self.center_window()
        self.configure(fg_color=BG_COLOR)
        
        self.prompts = []
        self.current_category = "Todos"
        
        self.build_ui()
        self.load_prompts()
        
        self.withdraw()
        self.is_visible = False
        self.animating = False
        
        self.setup_hotkey()

    def center_window(self):
        self.update_idletasks()
        width, height = 600, 550
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def stop_move(self, event):
        self._x = None
        self._y = None

    def do_move(self, event):
        try:
            x = self.winfo_x() + event.x - self._x
            y = self.winfo_y() + event.y - self._y
            self.geometry(f"+{x}+{y}")
        except AttributeError:
            pass

    def build_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, border_width=1, border_color=BORDER_COLOR, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=40)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="Promper", font=("Inter", 16, "bold"), text_color=FG_COLOR)
        self.title_label.pack(side="left", padx=5)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        
        self.add_btn = ctk.CTkButton(self.header_frame, text="➕", width=30, height=30, fg_color="transparent", hover_color=PRIMARY_COLOR, command=self.add_new_prompt)
        self.add_btn.pack(side="right", padx=5)
        
        self.close_btn = ctk.CTkButton(self.header_frame, text="✕", width=30, height=30, 
                                       fg_color="transparent", hover_color=BORDER_COLOR, 
                                       text_color=FG_COLOR, command=self.hide_window_animated)
        self.close_btn.pack(side="right")
        
        # Tabs for Categories
        self.tabview = ctk.CTkTabview(self.main_frame, fg_color="transparent", segmented_button_fg_color=CARD_COLOR, segmented_button_selected_color=PRIMARY_COLOR, segmented_button_selected_hover_color="#6342cc")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        
        # Search Entry inside each tab will be handled dynamically or we can put one global search above tabs
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.refresh_list)
        self.search_entry = ctk.CTkEntry(
            self.main_frame, textvariable=self.search_var, placeholder_text="Buscar prompt...",
            font=("Inter", 14), height=40, fg_color=CARD_COLOR, border_color=BORDER_COLOR, text_color=FG_COLOR
        )
        self.search_entry.pack(fill="x", padx=15, pady=(0, 15), before=self.tabview)
        
        self.search_entry.bind("<Return>", self.on_enter_search)
        self.bind("<Escape>", lambda e: self.hide_window_animated())
        
        self.scroll_areas = {} # dict of tab_name -> scrollable frame
        self.prompt_items = []

    def populate_tabs(self):
        # Clear existing tabs
        for tab in list(self.tabview._name_list):
            self.tabview.delete(tab)
        self.scroll_areas.clear()
        
        categories = ["Todos"]
        cats = sorted(list(set([p.get("category", "General") for p in self.prompts if not p.get("archived", False)])))
        categories.extend(cats)
        categories.append("Archivados")
        
        for cat in categories:
            self.tabview.add(cat)
            scroll = ctk.CTkScrollableFrame(self.tabview.tab(cat), fg_color="transparent")
            scroll.pack(fill="both", expand=True)
            self.scroll_areas[cat] = scroll
            
        # Select first tab by default or remember selection
        try:
            if self.current_category in categories:
                self.tabview.set(self.current_category)
            else:
                self.tabview.set("Todos")
        except:
            self.tabview.set("Todos")
            
        # Command when switching tabs
        self.tabview.configure(command=self.on_tab_change)

    def on_tab_change(self):
        self.current_category = self.tabview.get()
        self.refresh_list()

    def update_prompts_file(self):
        with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.prompts, f, indent=4, ensure_ascii=False)
        self.load_prompts() # Reload to recreate UI correctly

    def load_prompts(self):
        if not os.path.exists(PROMPTS_FILE):
            default_prompts = []
            with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_prompts, f, indent=4)
                
        try:
            with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
                self.prompts = json.load(f)
                
            # Ensure UUIDs and schemas
            changed = False
            for p in self.prompts:
                if "id" not in p:
                    p["id"] = str(uuid.uuid4())
                    changed = True
                if "category" not in p:
                    p["category"] = "General"
                    changed = True
                if "archived" not in p:
                    p["archived"] = False
                    changed = True
            
            if changed:
                self.update_prompts_file()
                
        except Exception as e:
            print(f"Error cargando prompts: {e}")
            self.prompts = []
            
        self.populate_tabs()
        self.refresh_list()

    def refresh_list(self, *args):
        # clear current category scroll area
        cat = self.tabview.get()
        if not cat:
            cat = self.current_category
            
        scroll_area = self.scroll_areas.get(cat)
        if not scroll_area: return
        
        for child in scroll_area.winfo_children():
            child.destroy()
            
        query = self.search_var.get().lower()
        
        filtered = []
        for p in self.prompts:
            is_archived = p.get("archived", False)
            if cat == "Archivados" and not is_archived:
                continue
            if cat != "Archivados" and is_archived:
                continue
            
            if cat != "Todos" and cat != "Archivados" and p.get("category", "") != cat:
                continue
                
            if query and query not in p.get("title", "").lower() and query not in p.get("text", "").lower():
                continue
                
            filtered.append(p)
            
        for p in filtered:
            item = PromptItem(
                scroll_area, p,
                command_execute=self.execute_prompt,
                command_edit=self.edit_prompt,
                command_delete=self.delete_prompt,
                command_archive=self.toggle_archive_prompt
            )
            item.pack(fill="x", pady=2)

    def on_enter_search(self, event):
        # find the first item dynamically matching the current constraints and execute it
        cat = self.tabview.get()
        query = self.search_var.get().lower()
        for p in self.prompts:
            is_archived = p.get("archived", False)
            if cat == "Archivados" and not is_archived: continue
            if cat != "Archivados" and is_archived: continue
            if cat != "Todos" and cat != "Archivados" and p.get("category", "") != cat: continue
            if query and query not in p.get("title", "").lower() and query not in p.get("text", "").lower(): continue
            self.execute_prompt(p.get("text", ""))
            break

    def execute_prompt(self, text):
        self.hide_window_animated()
        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')

    def add_new_prompt(self):
        EditDialog(self, on_save=self.save_prompt)
        
    def edit_prompt(self, prompt_data):
        EditDialog(self, prompt_data=prompt_data.copy(), on_save=self.save_prompt)

    def save_prompt(self, updated_prompt):
        # check if exists
        exists = False
        for i, p in enumerate(self.prompts):
            if p["id"] == updated_prompt["id"]:
                self.prompts[i] = updated_prompt
                exists = True
                break
        if not exists:
            self.prompts.append(updated_prompt)
        self.update_prompts_file()

    def delete_prompt(self, prompt_data):
        self.prompts = [p for p in self.prompts if p["id"] != prompt_data["id"]]
        self.update_prompts_file()

    def toggle_archive_prompt(self, prompt_data):
        for p in self.prompts:
            if p["id"] == prompt_data["id"]:
                p["archived"] = not p.get("archived", False)
                break
        self.update_prompts_file()

    # --- Animations ---
    def fade_in(self, alpha):
        if not self.is_visible or self.animating == "out": return
        alpha += 0.1
        self.attributes('-alpha', min(alpha, 1.0))
        if alpha < 1.0:
            self.after(15, self.fade_in, alpha)
        else:
            self.animating = False

    def fade_out(self, alpha):
        if self.is_visible or self.animating == "in": return
        alpha -= 0.1
        self.attributes('-alpha', max(alpha, 0.0))
        if alpha > 0.0:
            self.after(15, self.fade_out, alpha)
        else:
            self.withdraw()
            self.animating = False

    def show_window_animated(self):
        if self.is_visible: return
        
        self.attributes('-alpha', 0.0)
        self.deiconify()
        self.attributes('-topmost', True)
        
        self.load_prompts()
        if self.search_var.get() != "":
            self.search_var.set("") 
            
        self.focus_force()
        self.search_entry.focus_set()
        
        self.is_visible = True
        self.animating = "in"
        self.fade_in(0.0)

    def hide_window_animated(self):
        if not self.is_visible: return
        self.is_visible = False
        self.animating = "out"
        self.fade_out(self.attributes('-alpha'))

    def toggle_window(self):
        if self.is_visible:
            self.hide_window_animated()
        else:
            self.show_window_animated()

    def setup_hotkey(self):
        def listen():
            keyboard.add_hotkey('ctrl+alt+p', lambda: self.after(0, self.toggle_window))
            keyboard.wait()
        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()

if __name__ == "__main__":
    app = PromperApp()
    app.mainloop()
