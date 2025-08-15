import psycopg2
from tkinter import *
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from datetime import datetime
from ttkbootstrap.constants import *

# --- Database Functions ---
def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="bus_traffic_stats",
            user="postgres",
            password="2006",
            host="localhost",
            port="5432"
        )
        print("Connexion à la base de données réussie.")
    except psycopg2.Error as e:
        messagebox.showerror("Erreur de connexion", f"Erreur de connexion à la base de données: {e}\nL'application va se fermer.")
        return None
    return conn

def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn:
        return None, None
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        return cur, conn
    except psycopg2.Error as e:
        messagebox.showerror("Erreur de base de données", f"Erreur lors de l'exécution de la requête: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return None, None

def fetch_all_data(table_name, columns="*", where_clause=""):
    query = f"SELECT {columns} FROM {table_name} {where_clause}"
    cur, conn = execute_query(query)
    if cur:
        try:
            data = cur.fetchall()
            return data
        except psycopg2.Error as e:
            messagebox.showerror("Erreur de récupération", f"Erreur lors de la récupération des données: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    return []

def fetch_single_record(table_name, primary_key_column, primary_key_value):
    query = f"SELECT * FROM {table_name} WHERE {primary_key_column} = %s"
    cur, conn = execute_query(query, (primary_key_value,))
    if cur:
        try:
            record = cur.fetchone()
            return record
        except psycopg2.Error as e:
            messagebox.showerror("Erreur de récupération", f"Erreur lors de la récupération du l'enregistrement: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    return None

def insert_data(table_name, columns, values):
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)
    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    cur, conn = execute_query(query, tuple(values))
    if cur:
        cur.close()
        conn.close()
        return True
    return False

def update_data(table_name, set_clause, where_clause, values):
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
    cur, conn = execute_query(query, values)
    if cur:
        cur.close()
        conn.close()
        return True
    return False

def delete_data(table_name, where_clause, value):
    query = f"DELETE FROM {table_name} WHERE {where_clause}"
    cur, conn = execute_query(query, (value,))
    if cur:
        cur.close()
        conn.close()
        return True
    return False

class BusManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Gestion du Trafic des Bus - Agadir")
        self.root.geometry("1280x720")
        
        self.style = tb.Style(theme="yeti")
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'))

        self.conn = get_db_connection()
        if not self.conn:
            self.root.destroy()
            return
        
        self.conn.close()

        self.create_widgets()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.load_initial_data()
    
    def create_widgets(self):
        title_frame = tb.Frame(self.root, bootstyle=PRIMARY)
        title_frame.pack(fill=X, ipady=10, padx=10, pady=10)
        
        tb.Label(
            title_frame,
            text="SYSTÈME DE GESTION DU TRAFIC DES BUS - AGADIR",
            font=("Helvetica", 18, "bold"),
            bootstyle="inverse-primary"
        ).pack(pady=5)
        
        self.notebook = tb.Notebook(self.root, bootstyle=PRIMARY)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.create_bus_tab()
        self.create_lines_tab()
        self.create_stops_tab()
        self.create_trips_tab()
        self.create_stats_tab()
        
        self.status_bar = tb.Label(
            self.root,
            text="Prêt",
            relief=SUNKEN,
            anchor=W,
            bootstyle=(INFO, INVERSE)
        )
        self.status_bar.pack(fill=X, padx=10, pady=(0, 5))
        
    def create_treeview(self, parent, columns, visible_cols):
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        tree = tb.Treeview(parent, columns=columns, show="headings", bootstyle="primary")
        
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            if col in visible_cols:
                tree.column(col, anchor="center")
            else:
                tree.column(col, width=0, stretch=NO)
        
        scroll_y = tb.Scrollbar(parent, orient="vertical", command=tree.yview, bootstyle="secondary-round")
        scroll_x = tb.Scrollbar(parent, orient="horizontal", command=tree.xview, bootstyle="secondary-round")
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side=RIGHT, fill="y")
        scroll_x.pack(side=BOTTOM, fill="x")
        tree.pack(fill="both", expand=True)
        
        return tree
    
    def show_details_for_selected_item(self, tree, title_prefix):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un élément à afficher.")
            return

        visible_columns = {
            "Bus": ["bus_number", "capacity", "matricule"],
            "Lignes": ["line_number", "line_name", "origin", "destination", "distance_km"],
            "Arrêts": ["stop_name", "latitude", "longitude", "zone"],
            "Trajets": ["bus_number", "line_number", "driver_name", "start_datetime", "end_datetime", "passenger_count", "status", "stop_time"]
}
        
       
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        
  
        details_window = tb.Toplevel(self.root)
        details_window.title(f"Détails - {title_prefix}")
        details_window.geometry("500x400")
        
        
        main_frame = tb.Frame(details_window)
        main_frame.pack(fill=BOTH, expand=True)
        
        canvas = Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
          

        item_values = tree.item(selected_item, "values")
        columns = tree["columns"]
        
        for i, col in enumerate(columns):
            col_name = col
            col_header = tree.heading(col, "text")
            
         
            if current_tab in visible_columns and col_name in visible_columns[current_tab]:
                row_frame = tb.Frame(scrollable_frame)
                row_frame.pack(fill=X, padx=10, pady=5)
                
                tb.Label(
                    row_frame, 
                    text=f"{col_header}:",
                    font=("Helvetica", 10, "bold"),
                    width=20,
                    anchor="w"
                ).pack(side=LEFT)
                
                tb.Label(
                    row_frame,
                    text=item_values[i],
                    font=("Helvetica", 10)
                ).pack(side=LEFT)
        
     
        btn_frame = tb.Frame(details_window)
        btn_frame.pack(fill=X, pady=10)
        tb.Button(
            btn_frame, 
            text="Fermer", 
            command=details_window.destroy,
            bootstyle="danger"
        ).pack()

    def on_tab_change(self, event):
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab == "Statistiques":
            self.load_stats_data()
        else:
            self.load_initial_data(selected_tab)
            
    def load_initial_data(self, tab_name=None):
        if tab_name is None or tab_name == "Bus":
            self.load_bus_data()
        if tab_name is None or tab_name == "Lignes":
            self.load_line_data()
        if tab_name is None or tab_name == "Arrêts":
            self.load_stop_data()
        if tab_name is None or tab_name == "Trajets":
            self.load_trip_data()

    def clear_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def insert_data_to_treeview(self, tree, data):
        for row in data:
            tree.insert("", "end", values=row)

    # --- Bus Tab ---
    def create_bus_tab(self):
        self.bus_tab = tb.Frame(self.notebook)
        self.notebook.add(self.bus_tab, text="Bus")
        
        control_frame = tb.Frame(self.bus_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)
        
        button_frame = tb.Frame(control_frame)
        button_frame.pack(side=TOP, fill=X, pady=5)
        
        tb.Button(button_frame, text="Ajouter", command=self.show_bus_add_form, bootstyle=SUCCESS, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_bus, bootstyle=DANGER, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Modifier", command=self.show_bus_update_form, bootstyle=INFO, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Rechercher", command=self.show_bus_search_form, bootstyle=PRIMARY, width=10).pack(side=LEFT, padx=5)
        
        tb.Button(button_frame, text="Afficher", command=lambda: self.show_details_for_selected_item(self.bus_tree, "Détails du Bus"), bootstyle=SECONDARY, width=10).pack(side=LEFT, padx=5)
        
        self.bus_form_frame = tb.LabelFrame(control_frame, text="Formulaire Bus", bootstyle=INFO)
        self.bus_form_frame.pack_forget()
        
        form_grid = tb.Frame(self.bus_form_frame)
        form_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(form_grid, text="Numéro:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.bus_number_entry = tb.Entry(form_grid)
        self.bus_number_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(form_grid, text="Capacité:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.bus_capacity_entry = tb.Entry(form_grid)
        self.bus_capacity_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tb.Label(form_grid, text="Matricule:").grid(row=0, column=4, padx=5, pady=5, sticky=W)
        self.bus_matricule_entry = tb.Entry(form_grid)
        self.bus_matricule_entry.grid(row=0, column=5, padx=5, pady=5)
        
        self.bus_action_btn_frame = tb.Frame(self.bus_form_frame)
        self.bus_action_btn_frame.pack(fill=X, pady=5)
        
        self.bus_search_frame = tb.LabelFrame(control_frame, text="Recherche", bootstyle=INFO)
        self.bus_search_frame.pack_forget()
        
        search_grid = tb.Frame(self.bus_search_frame)
        search_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(search_grid, text="Numéro Bus:").pack(side=LEFT, padx=5)
        self.bus_search_entry = tb.Entry(search_grid)
        self.bus_search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        tb.Button(search_grid, text="Chercher", command=self.search_bus, bootstyle=(SECONDARY, OUTLINE)).pack(side=LEFT, padx=5)
        
        tree_frame = tb.Frame(self.bus_tab)
        tree_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.bus_tree = self.create_treeview(tree_frame, ["id_bus","bus_number", "capacity", "matricule"], ["bus_number"])

    def show_bus_add_form(self):
        self.hide_all_bus_frames()
        self.bus_form_frame.pack(side=TOP, fill=X, pady=5)
        self.clear_bus_entries()
        self.update_bus_action_buttons(self.add_bus, "Confirmer l'ajout", SUCCESS)
    
    def show_bus_update_form(self):
        selected_item = self.bus_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un bus à modifier.")
            return

        self.hide_all_bus_frames()
        self.bus_form_frame.pack(side=TOP, fill=X, pady=5)
        self.update_bus_action_buttons(self.update_bus, "Confirmer la modification", INFO)
        
        bus_id_to_find = self.bus_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT * FROM bus WHERE id_bus = %s", (bus_id_to_find,))
                record = cur.fetchone()
                if record:
                    self.clear_bus_entries()
                    self.bus_number_entry.insert(0, record[1])
                    self.bus_capacity_entry.insert(0, record[2])
                    self.bus_matricule_entry.insert(0, record[3])
                else:
                    messagebox.showerror("Erreur", "Bus non trouvé dans la base de données.")
            finally:
                cur.close()
                conn.close()

    def show_bus_search_form(self):
        self.hide_all_bus_frames()
        self.bus_search_frame.pack(side=TOP, fill=X, pady=5)
    
    def hide_all_bus_frames(self):
        self.bus_form_frame.pack_forget()
        self.bus_search_frame.pack_forget()

    def update_bus_action_buttons(self, command, text, bootstyle):
        for widget in self.bus_action_btn_frame.winfo_children():
            widget.destroy()
        tb.Button(self.bus_action_btn_frame, text=text, command=command, bootstyle=bootstyle).pack(pady=5)
    
    def add_bus(self):
        bus_number = self.bus_number_entry.get()
        capacity = self.bus_capacity_entry.get()
        matricule = self.bus_matricule_entry.get()
        if insert_data("bus", ["bus_number", "capacity", "matricule"], [bus_number, capacity, matricule]):
            messagebox.showinfo("Succès", "Bus ajouté avec succès.")
            self.load_bus_data()
            self.hide_all_bus_frames()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout du bus.")

    def update_bus(self):
        selected_item = self.bus_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un bus à modifier.")
            return

        bus_id = self.bus_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            bus_number = self.bus_number_entry.get()
            capacity = self.bus_capacity_entry.get()
            matricule = self.bus_matricule_entry.get()
            set_clause = "bus_number=%s, capacity=%s, matricule=%s"
            where_clause = "id_bus=%s"
            values = (bus_number, capacity, matricule, bus_id)
            if update_data("bus", set_clause, where_clause, values):
                messagebox.showinfo("Succès", "Bus modifié avec succès.")
                self.load_bus_data()
                self.hide_all_bus_frames()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification du bus.")
        finally:
            cur.close()
            conn.close()
            
    def delete_bus(self):
        selected_item = self.bus_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un bus à supprimer.")
            return

        bus_id = self.bus_tree.item(selected_item, "values")[0]
        bus_number = self.bus_tree.item(selected_item, "values")[1]
        
        conn = get_db_connection()
        if not conn: return
        
        try:
            cur = conn.cursor()
            
            # التحقق من وجود رحلات مرتبطة
            cur.execute("SELECT COUNT(*) FROM trip WHERE id_bus = %s", (bus_id,))
            trip_count = cur.fetchone()[0]
            
            if trip_count > 0:
                # عرض خيارات للمستخدم
                choice = messagebox.askyesnocancel(
                    "Trajets associés",
                    f"Ce bus ({bus_number}) a {trip_count} trajets associés.\n"
                    "Voulez-vous supprimer aussi tous les trajets associés?\n\n"
                    "Oui - Supprimer le bus et ses trajets\n"
                    "Non - Supprimer seulement le bus (si possible)\n"
                    "Annuler - Ne rien supprimer"
                )
                
                if choice is None:  # Annuler
                    return
                elif choice:   
                    try:
                        cur.execute("DELETE FROM trip WHERE id_bus = %s", (bus_id,))
                        cur.execute("DELETE FROM bus WHERE id_bus = %s", (bus_id,))
                        conn.commit()
                        messagebox.showinfo("Succès", f"Bus {bus_number} et {trip_count} trajets associés supprimés.")
                        self.load_bus_data()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Erreur", f"Erreur lors de la suppression: {e}")
                else:  # Non - محاولة حذف الحافلة فقط
                    try:
                        cur.execute("DELETE FROM bus WHERE id_bus = %s", (bus_id,))
                        conn.commit()
                        messagebox.showinfo("Succès", f"Bus {bus_number} supprimé.")
                        self.load_bus_data()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Erreur", 
                            f"Impossible de supprimer le bus seul: {e}\n"
                            "Il existe probablement des contraintes de clé étrangère.")
            else:
                if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le bus {bus_number}?"):
                    cur.execute("DELETE FROM bus WHERE id_bus = %s", (bus_id,))
                    conn.commit()
                    messagebox.showinfo("Succès", "Bus supprimé avec succès.")
                    self.load_bus_data()
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
            conn.rollback()
        finally:
            conn.close()

    def search_bus(self):
        search_term = self.bus_search_entry.get()
        if not search_term:
            self.load_bus_data()
            return
        
        self.clear_treeview(self.bus_tree)
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                query = "SELECT id_bus, bus_number, capacity, matricule FROM bus WHERE bus_number::text LIKE %s"
                cur.execute(query, (f"%{search_term}%",))
                data = cur.fetchall()
                self.insert_data_to_treeview(self.bus_tree, data)
                self.status_bar.config(text=f"Recherche de bus terminée. {len(data)} résultats trouvés.")
            except psycopg2.Error as e:
                messagebox.showerror("Erreur de recherche", f"Erreur lors de la recherche: {e}")
            finally:
                cur.close()
                conn.close()

    def load_bus_data(self):
        self.clear_treeview(self.bus_tree)
        data = fetch_all_data("bus", columns="id_bus, bus_number, capacity, matricule")
        self.insert_data_to_treeview(self.bus_tree, data)
        self.status_bar.config(text="Affichage des données des bus terminé.")

    def clear_bus_entries(self):
        self.bus_number_entry.delete(0, END)
        self.bus_capacity_entry.delete(0, END)
        self.bus_matricule_entry.delete(0, END)

    # --- Lines Tab ---
    def create_lines_tab(self):
        self.lines_tab = tb.Frame(self.notebook)
        self.notebook.add(self.lines_tab, text="Lignes")
        
        control_frame = tb.Frame(self.lines_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)
        
        button_frame = tb.Frame(control_frame)
        button_frame.pack(side=TOP, fill=X, pady=5)
        
        tb.Button(button_frame, text="Ajouter", command=self.show_line_add_form, bootstyle=SUCCESS, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_line, bootstyle=DANGER, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Modifier", command=self.show_line_update_form, bootstyle=INFO, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Rechercher", command=self.show_line_search_form, bootstyle=PRIMARY, width=10).pack(side=LEFT, padx=5)

        tb.Button(button_frame, text="Afficher", command=lambda: self.show_details_for_selected_item(self.lines_tree, "Détails de la Ligne"), bootstyle=SECONDARY, width=10).pack(side=LEFT, padx=5)
        
        self.line_form_frame = tb.LabelFrame(control_frame, text="Formulaire Ligne", bootstyle=INFO)
        self.line_form_frame.pack_forget()

        form_grid = tb.Frame(self.line_form_frame)
        form_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(form_grid, text="Numéro Ligne:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.line_number_entry = tb.Entry(form_grid)
        self.line_number_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(form_grid, text="Nom Ligne:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.line_name_entry = tb.Entry(form_grid)
        self.line_name_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tb.Label(form_grid, text="Départ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.line_origin_entry = tb.Entry(form_grid)
        self.line_origin_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tb.Label(form_grid, text="Arrivée:").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.line_destination_entry = tb.Entry(form_grid)
        self.line_destination_entry.grid(row=1, column=3, padx=5, pady=5)
        
        tb.Label(form_grid, text="Distance (km):").grid(row=1, column=4, padx=5, pady=5, sticky=W)
        self.line_distance_entry = tb.Entry(form_grid)
        self.line_distance_entry.grid(row=1, column=5, padx=5, pady=5)
        
        self.line_action_btn_frame = tb.Frame(self.line_form_frame)
        self.line_action_btn_frame.pack(fill=X, pady=5)

        self.line_search_frame = tb.LabelFrame(control_frame, text="Recherche", bootstyle=INFO)
        self.line_search_frame.pack_forget()
        
        search_grid = tb.Frame(self.line_search_frame)
        search_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(search_grid, text="Numéro Ligne:").pack(side=LEFT, padx=5)
        self.line_search_entry = tb.Entry(search_grid)
        self.line_search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        tb.Button(search_grid, text="Chercher", command=self.search_line, bootstyle=(SECONDARY, OUTLINE)).pack(side=LEFT, padx=5)
        
        tree_frame = tb.Frame(self.lines_tab)
        tree_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.lines_tree = self.create_treeview(tree_frame, ["id_line", "line_number", "line_name", "origin", "destination", "distance_km"], ["line_number"])
        
    def show_line_add_form(self):
        self.hide_all_line_frames()
        self.line_form_frame.pack(side=TOP, fill=X, pady=5)
        self.clear_line_entries()
        self.update_line_action_buttons(self.add_line, "Confirmer l'ajout", SUCCESS)

    def show_line_update_form(self):
        selected_item = self.lines_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner une ligne à modifier.")
            return

        self.hide_all_line_frames()
        self.line_form_frame.pack(side=TOP, fill=X, pady=5)
        self.update_line_action_buttons(self.update_line, "Confirmer la modification", INFO)
        
        line_id_to_find = self.lines_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT * FROM bus_line WHERE id_line = %s", (line_id_to_find,))
                record = cur.fetchone()
                if record:
                    self.clear_line_entries()
                    self.line_number_entry.insert(0, record[1])
                    self.line_name_entry.insert(0, record[2])
                    self.line_origin_entry.insert(0, record[3])
                    self.line_destination_entry.insert(0, record[4])
                    self.line_distance_entry.insert(0, record[5])
                else:
                    messagebox.showerror("Erreur", "Ligne non trouvée dans la base de données.")
            finally:
                cur.close()
                conn.close()

    def show_line_search_form(self):
        self.hide_all_line_frames()
        self.line_search_frame.pack(side=TOP, fill=X, pady=5)
    
    def hide_all_line_frames(self):
        self.line_form_frame.pack_forget()
        self.line_search_frame.pack_forget()

    def update_line_action_buttons(self, command, text, bootstyle):
        for widget in self.line_action_btn_frame.winfo_children():
            widget.destroy()
        tb.Button(self.line_action_btn_frame, text=text, command=command, bootstyle=bootstyle).pack(pady=5)
    
    def add_line(self):
        line_number = self.line_number_entry.get()
        line_name = self.line_name_entry.get()
        origin = self.line_origin_entry.get()
        destination = self.line_destination_entry.get()
        distance = self.line_distance_entry.get()
        columns = ["line_number", "line_name", "origin", "destination", "distance_km"]
        values = [line_number, line_name, origin, destination, distance]
        if insert_data("bus_line", columns, values):
            messagebox.showinfo("Succès", "Ligne ajoutée avec succès.")
            self.load_line_data()
            self.hide_all_line_frames()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout de la ligne.")

    def update_line(self):
        selected_item = self.lines_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner une ligne à modifier.")
            return

        line_id = self.lines_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            line_number = self.line_number_entry.get()
            line_name = self.line_name_entry.get()
            origin = self.line_origin_entry.get()
            destination = self.line_destination_entry.get()
            distance = self.line_distance_entry.get()
            set_clause = "line_number=%s, line_name=%s, origin=%s, destination=%s, distance_km=%s"
            where_clause = "id_line=%s"
            values = (line_number, line_name, origin, destination, distance, line_id)
            if update_data("bus_line", set_clause, where_clause, values):
                messagebox.showinfo("Succès", "Ligne modifiée avec succès.")
                self.load_line_data()
                self.hide_all_line_frames()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification de la ligne.")
        finally:
            cur.close()
            conn.close()

    def delete_line(self):
        selected_item = self.lines_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner une ligne à supprimer.")
            return
        
        line_id = self.lines_tree.item(selected_item, "values")[0]
        line_number = self.lines_tree.item(selected_item, "values")[1]
        
        conn = get_db_connection()
        if not conn: return
        
        try:
            cur = conn.cursor()
            
            
            cur.execute("SELECT COUNT(*) FROM trip WHERE id_line = %s", (line_id,))
            trip_count = cur.fetchone()[0]
            
            if trip_count > 0:
                
                popup = tb.Toplevel(self.root)
                popup.title(f"Suppression de la ligne {line_number}")
                
                msg = tb.Label(popup, 
                    text=f"Impossible de supprimer cette ligne car elle a {trip_count} trajets associés.",
                    font=("Helvetica", 10))
                msg.pack(pady=10, padx=10)
                
                btn_frame = tb.Frame(popup)
                btn_frame.pack(pady=10)
                
                # زر لعرض الرحلات المرتبطة
                show_trips_btn = tb.Button(btn_frame, 
                    text="Afficher les trajets associés",
                    command=lambda: self.show_related_trips(line_id, popup),
                    bootstyle="info")
                show_trips_btn.pack(side=LEFT, padx=5)
                
                # زر إلغاء
                cancel_btn = tb.Button(btn_frame,
                    text="Annuler",
                    command=popup.destroy,
                    bootstyle="secondary")
                cancel_btn.pack(side=LEFT, padx=5)
            else:
                if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la ligne {line_number}?"):
                    cur.execute("DELETE FROM bus_line WHERE id_line = %s", (line_id,))
                    conn.commit()
                    messagebox.showinfo("Succès", "Ligne supprimée avec succès.")
                    self.load_line_data()
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def show_related_trips(self, line_id, parent_window):
        parent_window.destroy()
        
        trips_window = tb.Toplevel(self.root)
        trips_window.title("Trajets associés")
        trips_window.geometry("800x400")
        
        tree_frame = tb.Frame(trips_window)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        columns = ["id_trip", "bus_number", "driver_name", "start_datetime", "end_datetime"]
        tree = self.create_treeview(tree_frame, columns, columns)
        
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                query = """
                SELECT t.id_trip, b.bus_number, t.driver_name, t.start_datetime, t.end_datetime
                FROM trip t
                JOIN bus b ON t.id_bus = b.id_bus
                WHERE t.id_line = %s
                ORDER BY t.start_datetime DESC
                """
                cur.execute(query, (line_id,))
                data = cur.fetchall()
                
                for row in data:
                    tree.insert("", "end", values=row)
                    
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la récupération des trajets: {e}")
            finally:
                conn.close()
    
    def search_line(self):
        search_term = self.line_search_entry.get()
        if not search_term:
            self.load_line_data()
            return
            
        self.clear_treeview(self.lines_tree)
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                query = "SELECT id_line, line_number, line_name, origin, destination, distance_km FROM bus_line WHERE line_number::text LIKE %s"
                cur.execute(query, (f"%{search_term}%",))
                data = cur.fetchall()
                self.insert_data_to_treeview(self.lines_tree, data)
                self.status_bar.config(text=f"Recherche de ligne terminée. {len(data)} résultats trouvés.")
            except psycopg2.Error as e:
                messagebox.showerror("Erreur de recherche", f"Erreur lors de la recherche: {e}")
            finally:
                cur.close()
                conn.close()

    def load_line_data(self):
        self.clear_treeview(self.lines_tree)
        data = fetch_all_data("bus_line", columns="id_line, line_number, line_name, origin, destination, distance_km")
        self.insert_data_to_treeview(self.lines_tree, data)
        self.status_bar.config(text="Affichage des données des lignes terminé.")
    
    def clear_line_entries(self):
        self.line_number_entry.delete(0, END)
        self.line_name_entry.delete(0, END)
        self.line_origin_entry.delete(0, END)
        self.line_destination_entry.delete(0, END)
        self.line_distance_entry.delete(0, END)

    # --- Stops Tab ---
    def create_stops_tab(self):
        self.stops_tab = tb.Frame(self.notebook)
        self.notebook.add(self.stops_tab, text="Arrêts")
        
        control_frame = tb.Frame(self.stops_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)
        
        button_frame = tb.Frame(control_frame)
        button_frame.pack(side=TOP, fill=X, pady=5)

        tb.Button(button_frame, text="Ajouter", command=self.show_stop_add_form, bootstyle=SUCCESS, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_stop, bootstyle=DANGER, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Modifier", command=self.show_stop_update_form, bootstyle=INFO, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Rechercher", command=self.show_stop_search_form, bootstyle=PRIMARY, width=10).pack(side=LEFT, padx=5)

        tb.Button(button_frame, text="Afficher", command=lambda: self.show_details_for_selected_item(self.stops_tree, "Détails de l'Arrêt"), bootstyle=SECONDARY, width=10).pack(side=LEFT, padx=5)
        
        self.stop_form_frame = tb.LabelFrame(control_frame, text="Formulaire Arrêt", bootstyle=INFO)
        self.stop_form_frame.pack_forget()

        form_grid = tb.Frame(self.stop_form_frame)
        form_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(form_grid, text="Nom Arrêt:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.stop_name_entry = tb.Entry(form_grid)
        self.stop_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(form_grid, text="Latitude:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.stop_lat_entry = tb.Entry(form_grid)
        self.stop_lat_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tb.Label(form_grid, text="Longitude:").grid(row=0, column=4, padx=5, pady=5, sticky=W)
        self.stop_lon_entry = tb.Entry(form_grid)
        self.stop_lon_entry.grid(row=0, column=5, padx=5, pady=5)

        tb.Label(form_grid, text="Zone:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.stop_zone_entry = tb.Entry(form_grid)
        self.stop_zone_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.stop_action_btn_frame = tb.Frame(self.stop_form_frame)
        self.stop_action_btn_frame.pack(fill=X, pady=5)
        
        self.stop_search_frame = tb.LabelFrame(control_frame, text="Recherche", bootstyle=INFO)
        self.stop_search_frame.pack_forget()

        search_grid = tb.Frame(self.stop_search_frame)
        search_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(search_grid, text="Nom Arrêt:").pack(side=LEFT, padx=5)
        self.stop_search_entry = tb.Entry(search_grid)
        self.stop_search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        tb.Button(search_grid, text="Chercher", command=self.search_stop, bootstyle=(SECONDARY, OUTLINE)).pack(side=LEFT, padx=5)
        
        tree_frame = tb.Frame(self.stops_tab)
        tree_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.stops_tree = self.create_treeview(tree_frame, ["id_stop", "stop_name", "latitude", "longitude", "zone"], ["stop_name"])

    def show_stop_add_form(self):
        self.hide_all_stop_frames()
        self.stop_form_frame.pack(side=TOP, fill=X, pady=5)
        self.clear_stop_entries()
        self.update_stop_action_buttons(self.add_stop, "Confirmer l'ajout", SUCCESS)
        
    def show_stop_update_form(self):
        selected_item = self.stops_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un arrêt à modifier.")
            return

        self.hide_all_stop_frames()
        self.stop_form_frame.pack(side=TOP, fill=X, pady=5)
        self.update_stop_action_buttons(self.update_stop, "Confirmer la modification", INFO)
        
        stop_id_to_find = self.stops_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT * FROM stop WHERE id_stop = %s", (stop_id_to_find,))
                record = cur.fetchone()
                if record:
                    self.clear_stop_entries()
                    self.stop_name_entry.insert(0, record[1])
                    self.stop_lat_entry.insert(0, record[2])
                    self.stop_lon_entry.insert(0, record[3])
                    self.stop_zone_entry.insert(0, record[4])
                else:
                    messagebox.showerror("Erreur", "Arrêt non trouvé dans la base de données.")
            finally:
                cur.close()
                conn.close()
    
    def show_stop_search_form(self):
        self.hide_all_stop_frames()
        self.stop_search_frame.pack(side=TOP, fill=X, pady=5)
    
    def hide_all_stop_frames(self):
        self.stop_form_frame.pack_forget()
        self.stop_search_frame.pack_forget()

    def update_stop_action_buttons(self, command, text, bootstyle):
        for widget in self.stop_action_btn_frame.winfo_children():
            widget.destroy()
        tb.Button(self.stop_action_btn_frame, text=text, command=command, bootstyle=bootstyle).pack(pady=5)
    
    def add_stop(self):
        stop_name = self.stop_name_entry.get()
        latitude = self.stop_lat_entry.get()
        longitude = self.stop_lon_entry.get()
        zone = self.stop_zone_entry.get()
        columns = ["stop_name", "latitude", "longitude", "zone"]
        values = [stop_name, latitude, longitude, zone]
        if insert_data("stop", columns, values):
            messagebox.showinfo("Succès", "Arrêt ajouté avec succès.")
            self.load_stop_data()
            self.hide_all_stop_frames()
        else:
            messagebox.showerror("Erreur", "Erreur lors de l'ajout de l'arrêt.")

    def update_stop(self):
        selected_item = self.stops_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un arrêt à modifier.")
            return

        stop_id = self.stops_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            stop_name = self.stop_name_entry.get()
            latitude = self.stop_lat_entry.get()
            longitude = self.stop_lon_entry.get()
            zone = self.stop_zone_entry.get()
            set_clause = "stop_name=%s, latitude=%s, longitude=%s, zone=%s"
            where_clause = "id_stop=%s"
            values = (stop_name, latitude, longitude, zone, stop_id)
            if update_data("stop", set_clause, where_clause, values):
                messagebox.showinfo("Succès", "Arrêt modifié avec succès.")
                self.load_stop_data()
                self.hide_all_stop_frames()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification de l'arrêt.")
        finally:
            cur.close()
            conn.close()

    def delete_stop(self):
        selected_item = self.stops_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un arrêt à supprimer.")
            return

        stop_id_to_find = self.stops_tree.item(selected_item, "values")[0]
        conn = get_db_connection()
        if not conn: return
        cur = conn.cursor()
        try:
            if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer l'arrêt {stop_id_to_find}?"):
                cur.execute("DELETE FROM stop WHERE id_stop = %s", (stop_id_to_find,))
                conn.commit()
                messagebox.showinfo("Succès", "Arrêt supprimé avec succès.")
                self.load_stop_data()
            self.hide_all_stop_frames()
        except psycopg2.Error as e:
            messagebox.showerror("Erreur de suppression", f"Erreur lors de la suppression: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def search_stop(self):
        search_term = self.stop_search_entry.get()
        if not search_term:
            self.load_stop_data()
            return
            
        self.clear_treeview(self.stops_tree)
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                query = "SELECT id_stop, stop_name, latitude, longitude, zone FROM stop WHERE stop_name LIKE %s"
                cur.execute(query, (f"%{search_term}%",))
                data = cur.fetchall()
                self.insert_data_to_treeview(self.stops_tree, data)
                self.status_bar.config(text=f"Recherche d'arrêt terminée. {len(data)} résultats trouvés.")
            except psycopg2.Error as e:
                messagebox.showerror("Erreur de recherche", f"Erreur lors de la recherche: {e}")
            finally:
                cur.close()
                conn.close()

    def load_stop_data(self):
        self.clear_treeview(self.stops_tree)
        data = fetch_all_data("stop", columns="id_stop, stop_name, latitude, longitude, zone")
        self.insert_data_to_treeview(self.stops_tree, data)
        self.status_bar.config(text="Affichage des données des arrêts terminé.")
    
    def clear_stop_entries(self):
        self.stop_name_entry.delete(0, END)
        self.stop_lat_entry.delete(0, END)
        self.stop_lon_entry.delete(0, END)
        self.stop_zone_entry.delete(0, END)

    # --- Trips Tab ---
    def create_trips_tab(self):
        self.trips_tab = tb.Frame(self.notebook)
        self.notebook.add(self.trips_tab, text="Trajets")

        control_frame = tb.Frame(self.trips_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)

        button_frame = tb.Frame(control_frame)
        button_frame.pack(side=TOP, fill=X, pady=5)
        
        tb.Button(button_frame, text="Ajouter", command=self.show_trip_add_form, bootstyle=SUCCESS, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_trip, bootstyle=DANGER, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Modifier", command=self.show_trip_update_form, bootstyle=INFO, width=10).pack(side=LEFT, padx=5)
        tb.Button(button_frame, text="Rechercher", command=self.show_trip_search_form, bootstyle=PRIMARY, width=10).pack(side=LEFT, padx=5)
        
        tb.Button(button_frame, text="Afficher", command=lambda: self.show_details_for_selected_item(self.trips_tree, "Détails du Trajet"), bootstyle=SECONDARY, width=10).pack(side=LEFT, padx=5)
        
        self.trip_form_frame = tb.LabelFrame(control_frame, text="Formulaire Trajet", bootstyle=INFO)
        self.trip_form_frame.pack_forget()

        form_grid = tb.Frame(self.trip_form_frame)
        form_grid.pack(fill=X, padx=5, pady=5)

        tb.Label(form_grid, text="Bus:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.trip_bus_combobox = ttk.Combobox(form_grid, state="readonly")
        self.trip_bus_combobox.grid(row=0, column=1, padx=5, pady=5)

        tb.Label(form_grid, text="Ligne:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        self.trip_line_combobox = ttk.Combobox(form_grid, state="readonly")
        self.trip_line_combobox.grid(row=0, column=3, padx=5, pady=5)

        tb.Label(form_grid, text="Nom du chauffeur:").grid(row=0, column=4, padx=5, pady=5, sticky=W)
        self.trip_driver_entry = tb.Entry(form_grid)
        self.trip_driver_entry.grid(row=0, column=5, padx=5, pady=5)
        
        tb.Label(form_grid, text="Heure de départ (YYYY-MM-DD HH:MI:SS):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.trip_start_entry = tb.Entry(form_grid)
        self.trip_start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tb.Label(form_grid, text="Heure d'arrivée (YYYY-MM-DD HH:MI:SS):").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        self.trip_end_entry = tb.Entry(form_grid)
        self.trip_end_entry.grid(row=1, column=3, padx=5, pady=5)
        
        tb.Label(form_grid, text="Passagers:").grid(row=1, column=4, padx=5, pady=5, sticky=W)
        self.trip_passenger_entry = tb.Entry(form_grid)
        self.trip_passenger_entry.grid(row=1, column=5, padx=5, pady=5)

        self.trip_action_btn_frame = tb.Frame(self.trip_form_frame)
        self.trip_action_btn_frame.pack(fill=X, pady=5)
        
        self.trip_search_frame = tb.LabelFrame(control_frame, text="Recherche", bootstyle=INFO)
        self.trip_search_frame.pack_forget()
        
        search_grid = tb.Frame(self.trip_search_frame)
        search_grid.pack(fill=X, padx=5, pady=5)
        
        tb.Label(search_grid, text="Trajet:").pack(side=LEFT, padx=5)
        self.trip_search_entry = tb.Entry(search_grid)
        self.trip_search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        tb.Button(search_grid, text="Chercher", command=self.search_trip, bootstyle=(SECONDARY, OUTLINE)).pack(side=LEFT, padx=5)

        tree_frame = tb.Frame(self.trips_tab)
        tree_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.trips_tree = self.create_treeview(tree_frame, ["id_trip", "bus_number", "line_number", "driver_name", "start_datetime", "end_datetime","passenger_count","status","stop_time"], ["id_trip"])
        
    def show_trip_add_form(self):
        self.hide_all_trip_frames()
        self.trip_form_frame.pack(side=TOP, fill=X, pady=5)
        self.clear_trip_entries()
        self.populate_trip_comboboxes()
        self.update_trip_action_buttons(self.add_trip, "Confirmer l'ajout", SUCCESS)

    def show_trip_update_form(self):
        selected_item = self.trips_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un trajet à modifier.")
            return

        self.hide_all_trip_frames()
        self.trip_form_frame.pack(side=TOP, fill=X, pady=5)
        self.update_trip_action_buttons(self.update_trip, "Confirmer la modification", INFO)

        self.populate_trip_comboboxes()
        self.clear_trip_entries()
        
        item_values = self.trips_tree.item(selected_item, "values")
        trip_id = item_values[0]
        
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                cur.execute("SELECT id_bus, id_line, driver_name, start_datetime, end_datetime, passenger_count FROM trip WHERE id_trip = %s", (trip_id,))
                record = cur.fetchone()

                if record:
                    self.trip_bus_combobox.set(self.get_bus_number_by_id(record[0]))
                    self.trip_line_combobox.set(self.get_line_number_by_id(record[1]))
                    self.trip_driver_entry.insert(0, record[2])
                    self.trip_start_entry.insert(0, record[3])
                    self.trip_end_entry.insert(0, record[4])
                    self.trip_passenger_entry.insert(0, record[5])
                else:
                    messagebox.showerror("Erreur", "Trajet non trouvé dans la base de données.")
            finally:
                cur.close()
                conn.close()

    def show_trip_search_form(self):
        self.hide_all_trip_frames()
        self.trip_search_frame.pack(side=TOP, fill=X, pady=5)

    def hide_all_trip_frames(self):
        self.trip_form_frame.pack_forget()
        self.trip_search_frame.pack_forget()
        
    def update_trip_action_buttons(self, command, text, bootstyle):
        for widget in self.trip_action_btn_frame.winfo_children():
            widget.destroy()
        tb.Button(self.trip_action_btn_frame, text=text, command=command, bootstyle=bootstyle).pack(pady=5)

    def populate_trip_comboboxes(self):
        buses = fetch_all_data("bus", "id_bus, bus_number")
        lines = fetch_all_data("bus_line", "id_line, line_number")
        
        self.bus_ids = [item[0] for item in buses]
        self.bus_numbers = [item[1] for item in buses]
        self.line_ids = [item[0] for item in lines]
        self.line_numbers = [item[1] for item in lines]
        
        self.trip_bus_combobox['values'] = self.bus_numbers
        self.trip_line_combobox['values'] = self.line_numbers
        
        if self.bus_numbers:
            self.trip_bus_combobox.set(self.bus_numbers[0])
        if self.line_numbers:
            self.trip_line_combobox.set(self.line_numbers[0])
            
    def get_bus_id_by_number(self, bus_number):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        try:
            cur.execute("SELECT id_bus FROM bus WHERE bus_number = %s", (bus_number,))
            result = cur.fetchone()
            return result[0] if result else None
        finally:
            cur.close()
            conn.close()

    def get_bus_number_by_id(self, bus_id):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        try:
            cur.execute("SELECT bus_number FROM bus WHERE id_bus = %s", (bus_id,))
            result = cur.fetchone()
            return result[0] if result else None
        finally:
            cur.close()
            conn.close()

    def get_line_id_by_number(self, line_number):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        try:
            cur.execute("SELECT id_line FROM bus_line WHERE line_number = %s", (line_number,))
            result = cur.fetchone()
            return result[0] if result else None
        finally:
            cur.close()
            conn.close()

    def get_line_number_by_id(self, line_id):
        conn = get_db_connection()
        if not conn: return None
        cur = conn.cursor()
        try:
            cur.execute("SELECT line_number FROM bus_line WHERE id_line = %s", (line_id,))
            result = cur.fetchone()
            return result[0] if result else None
        finally:
            cur.close()
            conn.close()

    def add_trip(self):
        try:
            bus_number = self.trip_bus_combobox.get()
            line_number = self.trip_line_combobox.get()
            id_bus = self.get_bus_id_by_number(bus_number)
            id_line = self.get_line_id_by_number(line_number)
            
            if not id_bus or not id_line:
                messagebox.showerror("Erreur", "Bus ou ligne non valide")
                return
                
            driver_name = self.trip_driver_entry.get()
            start_datetime_str = self.trip_start_entry.get()
            end_datetime_str = self.trip_end_entry.get()
            passenger_count = self.trip_passenger_entry.get()

            start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")

            columns = ["id_bus", "id_line", "driver_name", "start_datetime", "end_datetime", "passenger_count"]
            values = [id_bus, id_line, driver_name, start_datetime, end_datetime, passenger_count]
            if insert_data("trip", columns, values):
                messagebox.showinfo("Succès", "Trajet ajouté avec succès.")
                self.load_trip_data()
                self.hide_all_trip_frames()
            else:
                messagebox.showerror("Erreur", "Erreur lors de l'ajout du trajet.")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de format de date ou de données: {e}. Veuillez vérifier les formats.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {e}")

    def update_trip(self):
        selected_item = self.trips_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un trajet à modifier.")
            return

        try:
            trip_id = self.trips_tree.item(selected_item, "values")[0]
            bus_number = self.trip_bus_combobox.get()
            line_number = self.trip_line_combobox.get()
            id_bus = self.get_bus_id_by_number(bus_number)
            id_line = self.get_line_id_by_number(line_number)
            
            if not id_bus or not id_line:
                messagebox.showerror("Erreur", "Bus ou ligne non valide")
                return
                
            driver_name = self.trip_driver_entry.get()
            start_datetime_str = self.trip_start_entry.get()
            end_datetime_str = self.trip_end_entry.get()
            passenger_count = self.trip_passenger_entry.get()

            start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(end_datetime_str, "%Y-%m-%d %H:%M:%S")

            set_clause = "id_bus=%s, id_line=%s, driver_name=%s, start_datetime=%s, end_datetime=%s, passenger_count=%s"
            where_clause = "id_trip=%s"
            values = (id_bus, id_line, driver_name, start_datetime, end_datetime, passenger_count, trip_id)
            if update_data("trip", set_clause, where_clause, values):
                messagebox.showinfo("Succès", "Trajet modifié avec succès.")
                self.load_trip_data()
                self.hide_all_trip_frames()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la modification du trajet.")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de format de date ou de données: {e}. Veuillez vérifier les formats.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {e}")
            
    def delete_trip(self):
        selected_item = self.trips_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un trajet à supprimer.")
            return
        try:
            trip_id = self.trips_tree.item(selected_item, "values")[0]
            if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le trajet {trip_id}?"):
                conn = get_db_connection()
                if not conn:
                    return
                cur = conn.cursor()
                try:
                    cur.execute("DELETE FROM trip WHERE id_trip = %s", (trip_id,))
                    conn.commit()
                    messagebox.showinfo("Succès", "Trajet supprimé avec succès.")
                    self.load_trip_data()
                except psycopg2.Error as e:
                    messagebox.showerror("Erreur de suppression", f"Erreur lors de la suppression: {e}")
                    conn.rollback()
                finally:
                    cur.close()
                    conn.close()
            self.hide_all_trip_frames()
        except IndexError:
            messagebox.showerror("Erreur", "ID de trajet non valide. Veuillez vous assurer que le Treeview affiche le bon ID.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite: {e}")

    def search_trip(self):
        search_term = self.trip_search_entry.get()
        if not search_term:
            self.load_trip_data()
            return
            
        self.clear_treeview(self.trips_tree)
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            try:
                query = """
                SELECT 
                    t.id_trip, 
                    b.bus_number, 
                    bl.line_number, 
                    t.driver_name, 
                    t.start_datetime, 
                    t.end_datetime, 
                    t.passenger_count, 
                    t.status, 
                    t.stop_time
                FROM trip t
                JOIN bus b ON t.id_bus = b.id_bus
                JOIN bus_line bl ON t.id_line = bl.id_line
                WHERE t.id_trip::text LIKE %s OR t.driver_name LIKE %s
                ORDER BY t.id_trip;
                """
                cur.execute(query, (f"%{search_term}%", f"%{search_term}%"))
                data = cur.fetchall()
                self.insert_data_to_treeview(self.trips_tree, data)
                self.status_bar.config(text=f"Recherche de trajet terminée. {len(data)} résultats trouvés.")
            except psycopg2.Error as e:
                messagebox.showerror("Erreur de recherche", f"Erreur lors de la recherche: {e}")
            finally:
                cur.close()
                conn.close()

    def load_trip_data(self):
        self.clear_treeview(self.trips_tree)
        query = """
        SELECT 
            t.id_trip,
            b.bus_number, 
            bl.line_number, 
            t.driver_name, 
            t.start_datetime, 
            t.end_datetime, 
            t.passenger_count, 
            t.status, 
            t.stop_time
        FROM trip t
        JOIN bus b ON t.id_bus = b.id_bus
        JOIN bus_line bl ON t.id_line = bl.id_line
        ORDER BY t.id_trip;
        """
        conn = get_db_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute(query)
            data = cur.fetchall()
            self.insert_data_to_treeview(self.trips_tree, data)
            self.status_bar.config(text="Affichage des données des trajets terminé.")
        except psycopg2.Error as e:
            messagebox.showerror("Erreur de base de données", f"Erreur lors de la récupération des données: {e}")
        finally:
            cur.close()
            conn.close()

    def clear_trip_entries(self):
        self.trip_bus_combobox.set('')
        self.trip_line_combobox.set('')
        self.trip_driver_entry.delete(0, END)
        self.trip_start_entry.delete(0, END)
        self.trip_end_entry.delete(0, END)
        self.trip_passenger_entry.delete(0, END)
        
    # --- Statistics Tab ---
    def create_stats_tab(self):
        self.stats_tab = tb.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Statistiques")
        
        # Main container with scrollbar
        main_container = tb.Frame(self.stats_tab)
        main_container.pack(fill=BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        tb.Label(
            scrollable_frame,
            text="Statistiques Avancées des Bus",
            font=("Helvetica", 16, "bold"),
            bootstyle=PRIMARY
        ).pack(pady=10, padx=10, fill=X)
        
        # Bus selection
        selection_frame = tb.Frame(scrollable_frame)
        selection_frame.pack(fill=X, padx=10, pady=5)
        
        tb.Label(selection_frame, text="Sélectionner un bus:").pack(side=LEFT, padx=5)
        self.bus_stats_combobox = ttk.Combobox(selection_frame, state="readonly")
        self.bus_stats_combobox.pack(side=LEFT, padx=5, expand=True, fill=X)
        self.bus_stats_combobox.bind("<<ComboboxSelected>>", self.load_bus_stats)
        
        refresh_btn = tb.Button(
            selection_frame,
            text="Actualiser",
            command=self.update_bus_list,
            bootstyle="info"
        )
        refresh_btn.pack(side=LEFT, padx=5)
        
        # Stats display area
        self.stats_display_frame = tb.Frame(scrollable_frame)
        self.stats_display_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Initialize bus list
        self.update_bus_list()

    def update_bus_list(self):
        """Update the list of available buses"""
        buses = fetch_all_data("bus", "bus_number")
        if buses:
            bus_numbers = [bus[0] for bus in buses]
            self.bus_stats_combobox['values'] = bus_numbers
            if bus_numbers:
                self.bus_stats_combobox.set(bus_numbers[0])
                self.load_bus_stats()
        else:
            messagebox.showwarning("Aucun bus", "Aucun bus trouvé dans la base de données")

    def load_bus_stats(self, event=None):
        """Load statistics for the selected bus"""
        bus_number = self.bus_stats_combobox.get()
        if not bus_number:
            return
            
        # Clear previous stats
        for widget in self.stats_display_frame.winfo_children():
            widget.destroy()
            
        conn = get_db_connection()
        if not conn:
            return
            
        try:
            cur = conn.cursor()
            
            # Get bus info
            cur.execute("SELECT id_bus, capacity, matricule FROM bus WHERE bus_number = %s", (bus_number,))
            bus_info = cur.fetchone()
            
            if not bus_info:
                tb.Label(
                    self.stats_display_frame,
                    text=f"Aucune information trouvée pour le bus {bus_number}",
                    bootstyle="danger"
                ).pack(pady=10)
                return
                
            bus_id, capacity, matricule = bus_info
            
            # Bus info card
            info_card = tb.LabelFrame(
                self.stats_display_frame,
                text=f"Informations du Bus {bus_number}",
                bootstyle="info"
            )
            info_card.pack(fill=X, padx=5, pady=5)
            
            info_grid = tb.Frame(info_card)
            info_grid.pack(fill=X, padx=5, pady=5)
            
            tb.Label(info_grid, text="Matricule:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=W)
            tb.Label(info_grid, text=matricule).grid(row=0, column=1, sticky=W)
            
            tb.Label(info_grid, text="Capacité:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky=W)
            tb.Label(info_grid, text=f"{capacity} passagers").grid(row=1, column=1, sticky=W)
            
            # Trips statistics
            stats_card = tb.LabelFrame(
                self.stats_display_frame,
                text="Statistiques des Trajets",
                bootstyle="primary"
            )
            stats_card.pack(fill=X, padx=5, pady=5)
            
            # Total trips
            cur.execute("SELECT COUNT(*) FROM trip WHERE id_bus = %s", (bus_id,))
            total_trips = cur.fetchone()[0]
            self.create_stat_row(stats_card, "Nombre total de trajets:", f"{total_trips}")
            
            # Average passengers
            cur.execute("""
                SELECT AVG(passenger_count) 
                FROM trip 
                WHERE id_bus = %s AND passenger_count IS NOT NULL
            """, (bus_id,))
            avg_passengers = cur.fetchone()[0] or 0
            self.create_stat_row(stats_card, "Moyenne de passagers par trajet:", f"{avg_passengers:.1f}")
            
            # Occupancy rate
            if capacity > 0:
                occupancy_rate = (avg_passengers / capacity) * 100
                self.create_stat_row(stats_card, "Taux d'occupation moyen:", f"{occupancy_rate:.1f}%")
            
            # Most frequent line
            cur.execute("""
                SELECT bl.line_name, COUNT(*) as trip_count 
                FROM trip t 
                JOIN bus_line bl ON t.id_line = bl.id_line 
                WHERE t.id_bus = %s 
                GROUP BY bl.line_name 
                ORDER BY trip_count DESC 
                LIMIT 1
            """, (bus_id,))
            most_frequent_line = cur.fetchone()
            
            if most_frequent_line:
                line_frame = tb.Frame(stats_card)
                line_frame.pack(fill=X, pady=5)
                
                tb.Label(
                    line_frame, 
                    text="Ligne la plus fréquentée:", 
                    font=("Helvetica", 10, "bold")
                ).pack(side=LEFT)
                
                tb.Label(
                    line_frame, 
                    text=f"{most_frequent_line[0]} ({most_frequent_line[1]} trajets)"
                ).pack(side=LEFT, padx=5)
            
            # Last trip info
            cur.execute("""
                SELECT start_datetime, driver_name 
                FROM trip 
                WHERE id_bus = %s 
                ORDER BY start_datetime DESC 
                LIMIT 1
            """, (bus_id,))
            last_trip = cur.fetchone()
            
            if last_trip:
                trip_frame = tb.Frame(stats_card)
                trip_frame.pack(fill=X, pady=5)
                
                tb.Label(
                    trip_frame, 
                    text="Dernier trajet:", 
                    font=("Helvetica", 10, "bold")
                ).pack(side=LEFT)
                
                tb.Label(
                    trip_frame, 
                    text=f"Le {last_trip[0]} avec {last_trip[1]}"
                ).pack(side=LEFT, padx=5)
            
        except psycopg2.Error as e:
            messagebox.showerror("Erreur", f"Erreur de base de données: {e}")
        finally:
            cur.close()
            conn.close()

    def create_stat_row(self, parent, label, value):
        """Helper function to create a statistic row"""
        row = tb.Frame(parent)
        row.pack(fill=X, pady=2)
        
        tb.Label(
            row, 
            text=label, 
            font=("Helvetica", 10, "bold"),
            width=25,
            anchor="w"
        ).pack(side=LEFT)
        
        tb.Label(
            row, 
            text=value,
            font=("Helvetica", 10)
        ).pack(side=LEFT)

if __name__ == "__main__":
    root = tb.Window(themename="yeti")
    app = BusManagementApp(root)
    root.mainloop()