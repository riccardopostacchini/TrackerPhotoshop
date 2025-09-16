import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
import threading
import time
import json
import os
import sys
import ctypes
import pygetwindow as gw
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from collections import defaultdict

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ModernPhotoshopTracker:
    OUTPUT_FILE = "photoshop_times.json"
    SESSIONS_FILE = "sessions.json"
    SETTINGS_FILE = "settings.json"
    TAGS_FILE = "tags.json"
    POLL_INTERVAL = 2
    SESSION_GAP_THRESHOLD = 30 * 60  # 30 minuti in secondi

    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("650x650")

        self.tracked_times = {}
        self.all_tags = set()
        self.tag_ref_count = defaultdict(int)
        self.all_sessions = []
        self.current_session = None

        self.current_file = None
        self.start_time = None
        self.app_start_time = None
        self.running = True

        self.chart_canvas = None
        self.chart_figure = None
        self.chart_axes = None
        self.management_scroll_frame = None
        self.total_label = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar()
        self.sort_var = tk.StringVar()
        self.tab_view = None
        self.date_from_entry = None
        self.date_to_entry = None
        self.date_picker_frame = None
        self.tag_filter_frame = None
        self.tag_filter_menu = None
        self.session_scroll_frame = None

        self.settings = self._load_settings()
        self.translations = self._load_translations()
        self._set_language()
        self._set_theme()

        self._load_data()
        self._migrate_old_data_to_sessions()
        self._setup_ui()
        self._start_tracker()

    def _load_translations(self):
        return {
            "it": {
                "title": "Photoshop Time Tracker",
                "tab_live": "Sessione Attiva",
                "tab_chart": "Storico Grafico",
                "tab_manage": "Gestione Dati",
                "tab_sessions": "Sessioni",
                "tab_settings": "Impostazioni",
                "live_title": "Monitoraggio in Tempo Reale",
                "live_file": "File attivo: {}",
                "live_file_none": "File attivo: (nessuno)",
                "live_time": "Tempo totale su file: {}",
                "live_total_time": "Tempo totale sessione: {}",
                "manage_title": "Gestione File Tracciati",
                "manage_search": "Cerca:",
                "manage_placeholder": "Nome file...",
                "filter_options": ["Tutti", "Ultimi 7 giorni", "Ultimi 30 giorni", "Personalizzato", "Tag"],
                "sort_options": ["Piu tempo speso", "Usato piu di recente"],
                "date_from": "Da:",
                "date_to": "A:",
                "apply_btn": "Applica",
                "total_label": "Ore totali nel periodo: {}",
                "no_files": "Nessun file trovato.",
                "delete_btn": "Elimina",
                "delete_all_btn": "Elimina Tutti i Dati",
                "export_csv_btn": "Esporta CSV",
                "manage_tags_btn": "Gestisci Tag",
                "confirm_delete_title": "Conferma Eliminazione",
                "confirm_delete_msg": "Eliminare dati per:\n\n{}?",
                "confirm_delete_all_title": "Conferma Eliminazione Totale",
                "confirm_delete_all_msg": "Eliminare TUTTI i dati di tracciamento?",
                "settings_lang_label": "Lingua:",
                "settings_lang_it": "Italiano",
                "settings_lang_en": "English",
                "settings_theme_label": "Tema:",
                "settings_theme_dark": "Scuro",
                "settings_theme_light": "Chiaro",
                "chart_title": "File con Più Tempo Speso",
                "chart_xlabel": "Ore di Lavoro",
                "no_chart_data": "Nessun dato da visualizzare",
                "tag_window_title": "Gestione Tag per {}",
                "tag_new_placeholder": "Nuovo tag...",
                "tag_add_btn": "Aggiungi",
                "tag_remove_btn": "Rimuovi",
                "tag_select_placeholder": "Seleziona un tag esistente",
                "tag_add_selected_btn": "Aggiungi Selezionato",
                "tags_label": "Tags:",
                "no_tag_option": "Nessun tag",
                "sessions_title": "Storico Sessioni",
                "session_label": "Sessione #{} - {}",
                "session_active_time": "Tempo Attivo: {}",
                "session_total_time": "Tempo Totale: {}",
                "no_sessions": "Nessuna sessione trovata.",
                "session_details_title": "Dettagli Sessione #{}",
                "session_file_list_title": "File lavorati:",
                "file_time_label": "{} - {}"
            },
            "en": {
                "title": "Photoshop Time Tracker",
                "tab_live": "Active Session",
                "tab_chart": "Chart History",
                "tab_manage": "Data Management",
                "tab_sessions": "Sessions",
                "tab_settings": "Settings",
                "live_title": "Real-time Monitoring",
                "live_file": "Active file: {}",
                "live_file_none": "Active file: (none)",
                "live_time": "Total time on file: {}",
                "live_total_time": "Total session time: {}",
                "manage_title": "Tracked Files Management",
                "manage_search": "Search:",
                "manage_placeholder": "File name...",
                "filter_options": ["All", "Last 7 days", "Last 30 days", "Custom", "Tag"],
                "sort_options": ["Most time spent", "Most recently used"],
                "date_from": "From:",
                "date_to": "To:",
                "apply_btn": "Apply",
                "total_label": "Total hours in period: {}",
                "no_files": "No files found.",
                "delete_btn": "Delete",
                "delete_all_btn": "Delete All Data",
                "export_csv_btn": "Export CSV",
                "manage_tags_btn": "Manage Tags",
                "confirm_delete_title": "Confirm Deletion",
                "confirm_delete_msg": "Delete data for:\n\n{}?",
                "confirm_delete_all_title": "Confirm Total Deletion",
                "confirm_delete_all_msg": "Delete ALL tracking data?",
                "settings_lang_label": "Language:",
                "settings_lang_it": "Italiano",
                "settings_lang_en": "English",
                "settings_theme_label": "Theme:",
                "settings_theme_dark": "Dark",
                "settings_theme_light": "Light",
                "chart_title": "Files with Most Time Spent",
                "chart_xlabel": "Hours Worked",
                "no_chart_data": "No data to display",
                "tag_window_title": "Tag Management for {}",
                "tag_new_placeholder": "New tag...",
                "tag_add_btn": "Add",
                "tag_remove_btn": "Remove",
                "tag_select_placeholder": "Select an existing tag",
                "tag_add_selected_btn": "Add Selected",
                "tags_label": "Tags:",
                "no_tag_option": "No tag",
                "sessions_title": "Sessions History",
                "session_label": "Session #{} - {}",
                "session_active_time": "Active Time: {}",
                "session_total_time": "Total Time: {}",
                "no_sessions": "No sessions found.",
                "session_details_title": "Session Details #{}",
                "session_file_list_title": "Files worked on:",
                "file_time_label": "{} - {}"
            }
        }

    def _set_language(self):
        self.lang = self.settings.get("language", "it")
        self.t = self.translations[self.lang]

    def _set_theme(self):
        ctk.set_appearance_mode("Dark" if self.settings.get("theme") == "dark" else "Light")
        if sys.platform == "win32":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                value = ctypes.c_int(2)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(value), ctypes.sizeof(value)
                )
            except Exception:
                pass

    def _setup_ui(self):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, 'Icona.ico')
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            print(
                "Avviso: Impossibile caricare l'icona 'icon.ico'. Assicurati che il file esista nella stessa directory.")

        self.main_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        self.mono_font = ctk.CTkFont(family="Consolas", size=12)

        self.root.title(self.t["title"])
        self.tab_view = ctk.CTkTabview(self.root, fg_color="transparent")
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_view.add(self.t["tab_live"])
        self.tab_view.add(self.t["tab_chart"])
        self.tab_view.add(self.t["tab_manage"])
        self.tab_view.add(self.t["tab_sessions"])
        self.tab_view.add(self.t["tab_settings"])

        self.create_live_tab(self.tab_view.tab(self.t["tab_live"]))
        self.create_chart_tab(self.tab_view.tab(self.t["tab_chart"]))
        self.create_manage_tab(self.tab_view.tab(self.t["tab_manage"]))
        self.create_sessions_tab(self.tab_view.tab(self.t["tab_sessions"]))
        self.create_settings_tab(self.tab_view.tab(self.t["tab_settings"]))

        self.tab_view.configure(command=self._on_tab_change)
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def _load_data(self):
        self._load_settings()
        self._load_times()
        self._load_tags()
        self._load_sessions()

    def _start_tracker(self):
        threading.Thread(target=self._tracker_loop, daemon=True).start()
        self.update_gui()
        self.refresh_management_list()
        self.update_chart()
        self.refresh_session_list()

    def _on_tab_change(self):
        active_tab = self.tab_view.get()
        if active_tab == self.t["tab_chart"]:
            self.update_chart()
        elif active_tab == self.t["tab_manage"]:
            self.refresh_management_list()
        elif active_tab == self.t["tab_sessions"]:
            self.refresh_session_list()
        self.update_widget_colors()

    def create_live_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        self.live_tab_title = ctk.CTkLabel(frame, text=self.t["live_title"], font=self.title_font)
        self.live_tab_title.pack(pady=(0, 20))
        self.label_file = ctk.CTkLabel(frame, text=self.t["live_file_none"], font=self.main_font, wraplength=500)
        self.label_file.pack(pady=10)
        self.label_time = ctk.CTkLabel(frame, text=self.t["live_time"].format("0:00:00"), font=self.main_font)
        self.label_time.pack(pady=5)
        self.label_total_time = ctk.CTkLabel(frame, text=self.t["live_total_time"].format("0:00:00"),
                                             font=self.main_font)
        self.label_total_time.pack(pady=5)

    def create_chart_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=5, pady=10)
        current_theme = self.settings.get("theme", "dark")
        bgcolor = "#2B2B2B" if current_theme == "dark" else "white"
        self.chart_figure = Figure(figsize=(5, 4), dpi=100, facecolor=bgcolor)
        self.chart_axes = self.chart_figure.add_subplot(111)
        self.chart_canvas = FigureCanvasTkAgg(self.chart_figure, master=frame)
        self.chart_canvas.get_tk_widget().pack(expand=True, fill="both")

    def create_manage_tab(self, tab):
        self.manage_tab_title = ctk.CTkLabel(tab, text=self.t["manage_title"], font=self.title_font)
        self.manage_tab_title.pack(pady=(10, 5))
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.search_label = ctk.CTkLabel(search_frame, text=self.t["manage_search"], font=self.main_font)
        self.search_label.pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var,
                                         placeholder_text=self.t["manage_placeholder"])
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda _: self.refresh_management_list())

        filter_and_sort_frame = ctk.CTkFrame(tab, fg_color="transparent")
        filter_and_sort_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.filter_var.set(self.t["filter_options"][0])
        self.filter_menu = ctk.CTkOptionMenu(filter_and_sort_frame, values=self.t["filter_options"],
                                             variable=self.filter_var, command=self._show_filter_options)
        self.filter_menu.pack(side="left", padx=(0, 5), expand=True, fill="x")
        self.sort_var.set(self.t["sort_options"][0])
        self.sort_menu = ctk.CTkOptionMenu(filter_and_sort_frame, values=self.t["sort_options"], variable=self.sort_var,
                                           command=lambda _: self.refresh_management_list())
        self.sort_menu.pack(side="right", padx=(5, 0), expand=True, fill="x")

        self.date_picker_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.date_picker_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.date_picker_frame.pack_forget()
        ctk.CTkLabel(self.date_picker_frame, text=self.t["date_from"]).pack(side="left", padx=5)
        self.date_from_entry = DateEntry(self.date_picker_frame, date_pattern="yyyy-mm-dd", background="#2B2B2B",
                                         foreground="white", bordercolor="#555555", othermonthforeground="gray",
                                         selectbackground="blue")
        self.date_from_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.date_picker_frame, text=self.t["date_to"]).pack(side="left", padx=5)
        self.date_to_entry = DateEntry(self.date_picker_frame, date_pattern="yyyy-mm-dd", background="#2B2B2B",
                                       foreground="white", bordercolor="#555555", othermonthforeground="gray",
                                       selectbackground="blue")
        self.date_to_entry.pack(side="left", padx=5)
        ctk.CTkButton(self.date_picker_frame, text=self.t["apply_btn"],
                      command=lambda: (self.refresh_management_list(), self.update_chart())).pack(side="left", padx=5)

        self.tag_filter_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.tag_filter_frame.pack(fill="x", padx=10, pady=(0, 5))
        self.tag_filter_frame.pack_forget()
        ctk.CTkLabel(self.tag_filter_frame, text=self.t["tags_label"], font=self.main_font).pack(side="left",
                                                                                                 padx=(0, 5))

        self.management_scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.management_scroll_frame.pack(expand=True, fill="both", padx=10, pady=5)
        self.total_label = ctk.CTkLabel(tab, text=self.t["total_label"].format("0:00:00"), font=self.main_font)
        self.total_label.pack(pady=(0, 10))

        button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(button_frame, text=self.t["delete_all_btn"], command=self.delete_all_files, fg_color="#D2042D",
                      hover_color="#AA0022").pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(button_frame, text=self.t["export_csv_btn"], command=self.export_to_csv).pack(side="right",
                                                                                                    expand=True,
                                                                                                    fill="x",
                                                                                                    padx=(5, 0))

    def create_sessions_tab(self, tab):
        self.sessions_title = ctk.CTkLabel(tab, text=self.t["sessions_title"], font=self.title_font)
        self.sessions_title.pack(pady=(10, 5))
        self.session_scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.session_scroll_frame.pack(expand=True, fill="both", padx=10, pady=5)

    def create_settings_tab(self, tab):
        ctk.CTkLabel(tab, text=self.t["tab_settings"], font=self.title_font).pack(pady=(10, 20))
        ctk.CTkLabel(tab, text=self.t["settings_lang_label"], font=self.main_font).pack(anchor="w", padx=10)
        language_menu = ctk.CTkOptionMenu(tab, values=[self.t["settings_lang_it"], self.t["settings_lang_en"]],
                                          command=self._change_language)
        language_menu.set(self.t["settings_lang_it"] if self.lang == "it" else self.t["settings_lang_en"])
        language_menu.pack(padx=10, pady=5, fill="x")
        ctk.CTkLabel(tab, text=self.t["settings_theme_label"], font=self.main_font).pack(anchor="w", padx=10,
                                                                                         pady=(10, 0))
        theme_menu = ctk.CTkOptionMenu(tab, values=[self.t["settings_theme_dark"], self.t["settings_theme_light"]],
                                       command=self._change_theme)
        theme_menu.set(
            self.t["settings_theme_dark"] if self.settings.get("theme") == "dark" else self.t["settings_theme_light"])
        theme_menu.pack(padx=10, pady=5, fill="x")

    def _show_filter_options(self, choice):
        self.date_picker_frame.pack_forget()
        self.tag_filter_frame.pack_forget()
        if choice == self.t["filter_options"][3]:
            self.date_picker_frame.pack(fill="x", padx=10, pady=(0, 5))
        elif choice == self.t["filter_options"][4]:
            self.tag_filter_frame.pack(fill="x", padx=10, pady=(0, 5))
            self.update_tag_filter_menu()
        self.refresh_management_list()
        self.update_chart()

    def _change_language(self, choice):
        new_lang = "it" if choice == self.translations["it"]["settings_lang_it"] else "en"
        self.settings["language"] = new_lang
        self.save_settings()
        messagebox.showinfo("Info", "Riavvia l'app per applicare la nuova lingua.")

    def _change_theme(self, choice):
        new_theme = "dark" if choice == self.translations[self.lang]["settings_theme_dark"] else "light"
        self.settings["theme"] = new_theme
        self.save_settings()
        ctk.set_appearance_mode("Dark" if self.settings["theme"] == "dark" else "Light")
        self.update_widget_colors()
        self.update_chart()
        self.refresh_management_list()

    def update_widget_colors(self):
        theme = self.settings.get("theme", "dark")
        text_color = "white" if theme == "dark" else "black"
        for widget in self.root.winfo_children():
            if hasattr(widget, "configure"):
                try:
                    widget.configure(text_color=text_color)
                except Exception:
                    pass

    def _load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {"language": "it", "theme": "dark"}
        return {"language": "it", "theme": "dark"}

    def save_settings(self):
        with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def _load_times(self):
        if os.path.exists(self.OUTPUT_FILE):
            try:
                with open(self.OUTPUT_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for filename, file_data in data.items():
                        if "tags" not in file_data:
                            file_data["tags"] = []
                        for tag in file_data["tags"]:
                            self.tag_ref_count[tag] += 1
                        self.all_tags.update(file_data["tags"])
                    self.tracked_times = data
            except (json.JSONDecodeError, FileNotFoundError):
                self.tracked_times = {}

    def _load_tags(self):
        if os.path.exists(self.TAGS_FILE):
            try:
                with open(self.TAGS_FILE, "r", encoding="utf-8") as f:
                    self.all_tags = set(json.load(f))
            except (json.JSONDecodeError, FileNotFoundError):
                self.all_tags = set()

    def _load_sessions(self):
        if os.path.exists(self.SESSIONS_FILE):
            try:
                with open(self.SESSIONS_FILE, "r", encoding="utf-8") as f:
                    self.all_sessions = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.all_sessions = []

    def _migrate_old_data_to_sessions(self):
        if self.all_sessions:
            print("Sessioni esistenti trovate. Migrazione non necessaria.")
            return

        if not self.tracked_times:
            print("Nessun dato vecchio da migrare.")
            return

        print("Avvio migrazione dei dati vecchi in sessioni...")

        # Ordina i file in base alla data di ultima modifica
        sorted_files = sorted(self.tracked_times.items(), key=lambda item: item[1]['last_modified'])

        current_session = None
        for filename, data in sorted_files:
            file_start_time = data.get('start_time', data['last_modified'] - data['total_seconds'])
            file_end_time = data['last_modified']

            if current_session is None:
                # Inizia la prima sessione
                current_session = {
                    "start_time": file_start_time,
                    "end_time": file_end_time,
                    "active_seconds": data['total_seconds'],
                    "file_times": {filename: data['total_seconds']}
                }
            else:
                # Se il gap tra le sessioni è troppo grande, inizia una nuova sessione
                if file_start_time - current_session["end_time"] > self.SESSION_GAP_THRESHOLD:
                    current_session["total_seconds"] = current_session["end_time"] - current_session["start_time"]
                    self.all_sessions.append(current_session)
                    current_session = {
                        "start_time": file_start_time,
                        "end_time": file_end_time,
                        "active_seconds": data['total_seconds'],
                        "file_times": {filename: data['total_seconds']}
                    }
                else:
                    # Continua la sessione corrente
                    current_session["end_time"] = file_end_time
                    current_session["active_seconds"] += data['total_seconds']
                    current_session["file_times"][filename] = data['total_seconds']

        # Salva l'ultima sessione
        if current_session:
            current_session["total_seconds"] = current_session["end_time"] - current_session["start_time"]
            self.all_sessions.append(current_session)

        print(f"Migrazione completata. Create {len(self.all_sessions)} sessioni.")
        self._save_all_data()

    def _save_all_data(self):
        self._prune_tags()
        with open(self.OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tracked_times, f, indent=4, sort_keys=True)
        with open(self.TAGS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.all_tags), f, indent=4)
        with open(self.SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.all_sessions, f, indent=4)

    def _prune_tags(self):
        tags_to_remove = [tag for tag, count in self.tag_ref_count.items() if count <= 0]
        for tag in tags_to_remove:
            self.all_tags.discard(tag)
            del self.tag_ref_count[tag]

    def get_all_unique_tags(self):
        return sorted(list(self.all_tags))

    def update_tag_filter_menu(self):
        for widget in self.tag_filter_frame.winfo_children():
            if isinstance(widget, ctk.CTkOptionMenu):
                widget.destroy()
        all_tags = self.get_all_unique_tags()
        all_tags.insert(0, self.t["no_tag_option"])
        self.tag_filter_menu = ctk.CTkOptionMenu(self.tag_filter_frame, values=all_tags,
                                                 command=self.refresh_management_list)
        self.tag_filter_menu.set(all_tags[0])
        self.tag_filter_menu.pack(side="left", expand=True, fill="x", padx=(0, 5))

    def _get_filtered_and_sorted_files(self):
        results = []
        search_text = self.search_var.get().lower()
        selected_filter = self.filter_var.get()
        now = datetime.now()

        for filename, data in self.tracked_times.items():
            if search_text and search_text not in filename.lower():
                continue

            file_time = datetime.fromtimestamp(data.get("last_modified", time.time()))
            is_filtered = False

            if selected_filter == self.t["filter_options"][1] and file_time < now - timedelta(days=7):
                is_filtered = True
            elif selected_filter == self.t["filter_options"][2] and file_time < now - timedelta(days=30):
                is_filtered = True
            elif selected_filter == self.t["filter_options"][3]:
                try:
                    start = datetime.strptime(self.date_from_entry.get(), "%Y-%m-%d")
                    end = datetime.strptime(self.date_to_entry.get(), "%Y-%m-%d") + timedelta(days=1)
                    if not (start <= file_time < end):
                        is_filtered = True
                except ValueError:
                    is_filtered = True
            elif selected_filter == self.t["filter_options"][4]:
                selected_tag = self.tag_filter_menu.get() if self.tag_filter_menu else None
                if selected_tag == self.t["no_tag_option"]:
                    if data.get("tags"):
                        is_filtered = True
                elif selected_tag and selected_tag not in data.get("tags", []):
                    is_filtered = True
                if not selected_tag:
                    is_filtered = True

            if not is_filtered:
                results.append((filename, data))

        sort_by = self.sort_var.get()
        if sort_by == self.t["sort_options"][0]:
            results.sort(key=lambda x: x[1]["total_seconds"], reverse=True)
        elif sort_by == self.t["sort_options"][1]:
            results.sort(key=lambda x: x[1]["last_modified"], reverse=True)

        return results

    def refresh_management_list(self, *args):
        for widget in self.management_scroll_frame.winfo_children():
            widget.destroy()

        files = self._get_filtered_and_sorted_files()
        total_seconds = sum(d["total_seconds"] for _, d in files)
        text_color = "white" if self.settings.get("theme") == "dark" else "black"

        if not files:
            ctk.CTkLabel(self.management_scroll_frame, text=self.t["no_files"], font=self.main_font,
                         text_color=text_color).pack()
        else:
            for filename, data in files:
                row = ctk.CTkFrame(self.management_scroll_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                label_text = f"{filename[:30]:<30} | {self.format_time(data['total_seconds'])}"
                ctk.CTkLabel(row, text=label_text, font=self.mono_font, anchor="w", text_color=text_color).pack(
                    side="left", padx=10, expand=True, fill="x")
                button_frame_row = ctk.CTkFrame(row, fg_color="transparent")
                button_frame_row.pack(side="right")
                ctk.CTkButton(button_frame_row, text=self.t["manage_tags_btn"], width=100, fg_color="#555555",
                              command=lambda n=filename: self.manage_tags(n)).pack(side="left", padx=(0, 5))
                ctk.CTkButton(button_frame_row, text=self.t["delete_btn"], width=80, fg_color="#555555",
                              command=lambda n=filename: self.delete_file(n)).pack(side="right", padx=10)

        self.total_label.configure(text=self.t["total_label"].format(self.format_time(total_seconds)))

    def refresh_session_list(self):
        for widget in self.session_scroll_frame.winfo_children():
            widget.destroy()

        if not self.all_sessions:
            ctk.CTkLabel(self.session_scroll_frame, text=self.t["no_sessions"], font=self.main_font).pack(pady=20)
            return

        for i, session in enumerate(self.all_sessions):
            session_frame = ctk.CTkFrame(self.session_scroll_frame, corner_radius=10)
            session_frame.pack(fill="x", padx=10, pady=5)
            session_frame.bind("<Button-1>", lambda e, s=session, idx=i: self.show_session_details(s, idx + 1))

            start_date_str = datetime.fromtimestamp(session["start_time"]).strftime("%d/%m/%Y")
            session_label_text = self.t["session_label"].format(i + 1, start_date_str)

            label = ctk.CTkLabel(session_frame, text=session_label_text, font=self.main_font)
            label.pack(side="left", padx=10, pady=5)
            label.bind("<Button-1>", lambda e, s=session, idx=i: self.show_session_details(s, idx + 1))

            active_time_text = self.t["session_active_time"].format(self.format_time(session["active_seconds"]))
            active_time_label = ctk.CTkLabel(session_frame, text=active_time_text, font=self.main_font)
            active_time_label.pack(side="right", padx=10, pady=5)
            active_time_label.bind("<Button-1>", lambda e, s=session, idx=i: self.show_session_details(s, idx + 1))

            total_time_text = self.t["session_total_time"].format(self.format_time(session["total_seconds"]))
            total_time_label = ctk.CTkLabel(session_frame, text=total_time_text, font=self.main_font)
            total_time_label.pack(side="right", padx=10, pady=5)
            total_time_label.bind("<Button-1>", lambda e, s=session, idx=i: self.show_session_details(s, idx + 1))

    def show_session_details(self, session, session_number):
        details_window = ctk.CTkToplevel(self.root)
        details_window.title(self.t["session_details_title"].format(session_number))
        details_window.geometry("500x400")
        details_window.grab_set()

        ctk.CTkLabel(details_window, text=self.t["session_file_list_title"], font=self.title_font).pack(pady=10)

        file_scroll_frame = ctk.CTkScrollableFrame(details_window)
        file_scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        for filename, seconds in session["file_times"].items():
            file_label_text = self.t["file_time_label"].format(filename, self.format_time(seconds))
            ctk.CTkLabel(file_scroll_frame, text=file_label_text, font=self.main_font, anchor="w").pack(fill="x",
                                                                                                        padx=10, pady=2)

    def update_chart(self):
        files = self._get_filtered_and_sorted_files()
        self.chart_axes.clear()

        theme = self.settings.get("theme", "dark")
        textcolor = "white" if theme == "dark" else "black"
        bgcolor = "#2B2B2B" if theme == "dark" else "white"
        barcolor = "#1F6AA5" if theme == "dark" else "#0078D4"
        self.chart_figure.set_facecolor(bgcolor)
        self.chart_axes.set_facecolor(bgcolor)

        if not files:
            self.chart_axes.text(0.5, 0.5, self.t["no_chart_data"], ha='center', va='center', color=textcolor)
        else:
            sorted_times = sorted(files, key=lambda item: item[1]['total_seconds'])
            top_times = sorted_times[-10:]
            names = [n.replace(".psd", "")[:30] for n, _ in top_times]
            hours = [d['total_seconds'] / 3600 for _, d in top_times]
            self.chart_axes.barh(names, hours, color=barcolor)

        self.chart_axes.tick_params(axis='x', colors=textcolor)
        self.chart_axes.tick_params(axis='y', colors=textcolor)
        self.chart_axes.set_xlabel(self.t["chart_xlabel"], color=textcolor)
        self.chart_axes.set_title(self.t["chart_title"], color=textcolor)
        self.chart_figure.tight_layout()
        self.chart_canvas.draw_idle()

    @staticmethod
    def format_time(seconds):
        return str(timedelta(seconds=int(seconds)))

    def get_active_photoshop_file(self):
        try:
            active_window = gw.getActiveWindow()
            if active_window and ".psd" in active_window.title and "@" in active_window.title:
                return active_window.title.split("@")[0].strip()
        except Exception:
            return None
        return None

    def _tracker_loop(self):
        while self.running:
            active_file = self.get_active_photoshop_file()
            if active_file != self.current_file:
                self._handle_file_change(active_file)

            # Aggiorna il tempo attivo della sessione
            if self.app_start_time and active_file:
                self.current_session["active_seconds"] += self.POLL_INTERVAL

            time.sleep(self.POLL_INTERVAL)

    def _handle_file_change(self, new_file):
        self._save_current_file_time()

        # Inizia una nuova sessione se non è ancora iniziata
        if self.app_start_time is None and new_file:
            self.app_start_time = time.time()
            self.current_session = {
                "start_time": self.app_start_time,
                "end_time": None,
                "total_seconds": 0,
                "active_seconds": 0,
                "file_times": {}
            }

        if self.current_session:
            # Aggiorna il tempo totale della sessione
            self.current_session["total_seconds"] = time.time() - self.current_session["start_time"]

        self.current_file = new_file

        if new_file:
            if new_file not in self.tracked_times:
                self.tracked_times[new_file] = {"total_seconds": 0, "last_modified": time.time(),
                                                "start_time": time.time(), "tags": []}
            if new_file not in self.current_session["file_times"]:
                self.current_session["file_times"][new_file] = 0
            self.start_time = time.time()
        else:
            self.start_time = None

    def _save_current_file_time(self):
        if self.current_file and self.start_time:
            elapsed = time.time() - self.start_time
            self.tracked_times[self.current_file]["total_seconds"] += elapsed
            self.tracked_times[self.current_file]["last_modified"] = time.time()

            if self.current_session:
                self.current_session["file_times"][self.current_file] += elapsed

            self.start_time = None

    def _save_current_session_data(self):
        if self.current_session:
            self.current_session["end_time"] = time.time()
            self.current_session["total_seconds"] = self.current_session["end_time"] - self.current_session[
                "start_time"]
            self.all_sessions.append(self.current_session)
            self.current_session = None
            self.app_start_time = None

    def delete_file(self, filename_to_delete):
        if messagebox.askyesno(self.t["confirm_delete_title"], self.t["confirm_delete_msg"].format(filename_to_delete)):
            if filename_to_delete in self.tracked_times:
                for tag in self.tracked_times[filename_to_delete].get("tags", []):
                    self.tag_ref_count[tag] -= 1
                del self.tracked_times[filename_to_delete]
            self._save_all_data()
            self.refresh_management_list()
            self.update_chart()

    def delete_all_files(self):
        if messagebox.askyesno(self.t["confirm_delete_all_title"], self.t["confirm_delete_all_msg"]):
            self.tracked_times.clear()
            self.all_tags.clear()
            self.tag_ref_count.clear()
            self._save_all_data()
            self.refresh_management_list()
            self.update_chart()

    def export_to_csv(self):
        files = self._get_filtered_and_sorted_files()
        if not files:
            messagebox.showinfo("Esporta CSV", "Nessun file da esportare. Applica i filtri per visualizzare i file.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                                 title="Salva file CSV")
        if not file_path:
            return
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Nome File", "Data Inizio", "Ultimo Tracciamento"])
                for filename, data in files:
                    start_time = datetime.fromtimestamp(data.get("start_time", time.time()))
                    last_modified = datetime.fromtimestamp(data.get("last_modified", time.time()))
                    writer.writerow([filename, start_time.strftime("%d/%m/%Y %H:%M:%S"),
                                     last_modified.strftime("%d/%m/%Y %H:%M:%S")])
            messagebox.showinfo("Esporta CSV", f"Dati esportati con successo in:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Errore Esportazione", f"Si è verificato un errore durante l'esportazione: {e}")

    def manage_tags(self, filename):
        tag_window = ctk.CTkToplevel(self.root)
        tag_window.title(self.t["tag_window_title"].format(filename))
        tag_window.geometry("400x300")
        tag_window.grab_set()
        ctk.CTkLabel(tag_window, text=f"Tags per: {filename}", font=("Arial", 16, "bold")).pack(pady=10)
        tag_frame = ctk.CTkFrame(tag_window)
        tag_frame.pack(fill="both", expand=True, padx=10, pady=5)
        tag_list_frame = ctk.CTkScrollableFrame(tag_frame)
        tag_list_frame.pack(fill="both", expand=True, pady=5)

        def refresh_tag_list():
            for widget in tag_list_frame.winfo_children():
                widget.destroy()
            current_tags = self.tracked_times.get(filename, {}).get("tags", [])
            if not current_tags:
                ctk.CTkLabel(tag_list_frame, text="Nessun tag presente.").pack(pady=10)
            else:
                for tag in current_tags:
                    tag_row = ctk.CTkFrame(tag_list_frame, fg_color="transparent")
                    tag_row.pack(fill="x", pady=2)
                    ctk.CTkLabel(tag_row, text=tag, font=("Arial", 14), anchor="w").pack(side="left", fill="x",
                                                                                         expand=True, padx=5)
                    ctk.CTkButton(tag_row, text=self.t["tag_remove_btn"], width=80,
                                  command=lambda tag=tag: remove_tag(tag)).pack(side="right")
            update_existing_tags_menu()

        def add_tag():
            new_tag = tag_entry.get().strip()
            if new_tag and new_tag not in self.tracked_times.get(filename, {}).get("tags", []):
                self.all_tags.add(new_tag)
                self.tracked_times[filename]["tags"].append(new_tag)
                self.tag_ref_count[new_tag] += 1
                self._save_all_data()
                tag_entry.delete(0, "end")
                refresh_tag_list()
                self.refresh_management_list()

        def add_existing_tag():
            selected_tag = existing_tag_menu.get()
            if selected_tag and selected_tag != self.t["tag_select_placeholder"] and selected_tag not in \
                    self.tracked_times[filename]["tags"]:
                self.tracked_times[filename]["tags"].append(selected_tag)
                self.tag_ref_count[selected_tag] += 1
                self._save_all_data()
                refresh_tag_list()
                self.refresh_management_list()

        def remove_tag(tag):
            if tag in self.tracked_times[filename]["tags"]:
                self.tracked_times[filename]["tags"].remove(tag)
                self.tag_ref_count[tag] -= 1
                self._save_all_data()
                refresh_tag_list()
                self.refresh_management_list()

        def update_existing_tags_menu():
            existing_tags = [tag for tag in self.get_all_unique_tags() if
                             tag not in self.tracked_times.get(filename, {}).get("tags", [])]
            if not existing_tags:
                existing_tags = [self.t["tag_select_placeholder"]]
            existing_tag_menu.configure(values=existing_tags)
            existing_tag_menu.set(existing_tags[0])

        new_tag_frame = ctk.CTkFrame(tag_window, fg_color="transparent")
        new_tag_frame.pack(fill="x", padx=10, pady=(0, 5))
        tag_entry = ctk.CTkEntry(new_tag_frame, placeholder_text=self.t["tag_new_placeholder"], font=("Arial", 14))
        tag_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(new_tag_frame, text=self.t["tag_add_btn"], command=add_tag, width=80).pack(side="right")

        existing_tag_frame = ctk.CTkFrame(tag_window, fg_color="transparent")
        existing_tag_frame.pack(fill="x", padx=10, pady=(0, 10))
        existing_tag_menu = ctk.CTkOptionMenu(existing_tag_frame, values=[], font=("Arial", 14))
        existing_tag_menu.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(existing_tag_frame, text=self.t["tag_add_selected_btn"], command=add_existing_tag, width=80).pack(
            side="right")

        refresh_tag_list()

    def run(self):
        self.root.mainloop()

    def update_gui(self):
        if self.current_file:
            total_seconds = self.tracked_times.get(self.current_file, {}).get("total_seconds", 0)
            if self.start_time:
                total_seconds += time.time() - self.start_time
            self.label_file.configure(text=self.t["live_file"].format(self.current_file))
            self.label_time.configure(text=self.t["live_time"].format(self.format_time(total_seconds)))
        else:
            self.label_file.configure(text=self.t["live_file_none"])
            self.label_time.configure(text=self.t["live_time"].format("0:00:00"))

        if self.current_session:
            total_session_seconds = time.time() - self.current_session["start_time"]
            self.label_total_time.configure(
                text=self.t["live_total_time"].format(self.format_time(total_session_seconds)))
        else:
            self.label_total_time.configure(text=self.t["live_total_time"].format("0:00:00"))

        self.root.after(1000, self.update_gui)

    def stop(self):
        self.running = False
        self._save_current_file_time()
        self._save_current_session_data()
        self._save_all_data()
        self.root.after(100, self.root.destroy)


if __name__ == "__main__":
    app = ModernPhotoshopTracker()
    app.run()