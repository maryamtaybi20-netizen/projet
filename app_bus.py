import psycopg2
from tkinter import *
from tkinter import ttk, messagebox
import ttkbootstrap as tb # Importation de ttkbootstrap pour un style moderne
from threading import Thread

class BusManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion du Trafic des Bus - Système de Transport")
        self.root.geometry("1280x720")
        self.root.configure(bg="#f0f2f5")

        # Connexion à la base de données
        self.conn = self.connect_to_db()
        if not self.conn:
            self.root.destroy()
            return
        self.cur = self.conn.cursor()

        self.setup_styles()
        self.create_widgets()

    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                dbname="bus_traffic_stats",
                user="postgres",
                password="2006",
                host="localhost",
                port="5432"
            )
            return conn
        except psycopg2.OperationalError as e:
            messagebox.showerror("Erreur de connexion", 
                                 f"Impossible de se connecter à la base de données.\nErreur: {e}")
            return None

    def setup_styles(self):
        style = tb.Style(theme="yeti") # Utilisation du thème "yeti" de ttkbootstrap pour un look élégant

    def create_widgets(self):
        # Barre de titre principale
        title_frame = tb.Frame(self.root, bootstyle="primary")
        title_frame.pack(fill="x", ipady=10, padx=10, pady=10)
        tb.Label(title_frame, text="SYSTÈME DE GESTION DU TRAFIC DES BUS", 
                 font=("Helvetica", 18, "bold"), bootstyle="inverse-primary").pack(pady=5)

        # Onglets modernes
        self.notebook = tb.Notebook(self.root, bootstyle="primary")
        self.notebook.pack(pady=5, padx=10, expand=True, fill="both")

        self.bus_tab = tb.Frame(self.notebook, bootstyle="light")
        self.notebook.add(self.bus_tab, text="Bus")
        self.create_bus_widgets()

        self.lines_tab = tb.Frame(self.notebook, bootstyle="light")
        self.notebook.add(self.lines_tab, text="Lignes")
        self.create_lines_widgets()

        self.stops_tab = tb.Frame(self.notebook, bootstyle="light")
        self.notebook.add(self.stops_tab, text="Arrêts")
        self.create_stops_widgets()

        self.trips_tab = tb.Frame(self.notebook, bootstyle="light")
        self.notebook.add(self.trips_tab, text="Trajets")
        self.create_trips_widgets()

        self.stats_tab = tb.Frame(self.notebook, bootstyle="light")
        self.notebook.add(self.stats_tab, text="Statistiques")
        self.create_stats_widgets()

        # Barre de statut
        self.status_bar = tb.Label(self.root, text="Prêt", relief="sunken", anchor="w", bootstyle="info")
        self.status_bar.pack(fill="x", padx=10, pady=(0, 5))

    # --- Widgets pour la gestion des Bus ---
    def create_bus_widgets(self):
        control_frame = tb.Frame(self.bus_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)

        # Champ de recherche
        search_frame = tb.Frame(control_frame, bootstyle="light")
        search_frame.pack(side=tb.LEFT, padx=5, pady=5)
        tb.Label(search_frame, text="Rechercher:", bootstyle="secondary").pack(side=tb.LEFT)
        self.bus_search_entry = tb.Entry(search_frame, bootstyle="info")
        self.bus_search_entry.pack(side=tb.LEFT, padx=5)
        self.bus_search_entry.bind("<KeyRelease>", self.filter_bus_data)
        
        # Boutons
        button_frame = tb.Frame(control_frame, bootstyle="light")
        button_frame.pack(side=tb.RIGHT, padx=5, pady=5)
        tb.Button(button_frame, text="Afficher", command=self.display_all_buses, bootstyle="primary").pack(side=tb.LEFT, padx=5)
        tb.Button(button_frame, text="Ajouter", command=self.add_bus_window, bootstyle="success").pack(side=tb.LEFT, padx=5)
        tb.Button(button_frame, text="Modifier", command=self.edit_selected_bus, bootstyle="info").pack(side=tb.LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_selected_bus, bootstyle="danger").pack(side=tb.LEFT, padx=5)

        # Treeview avec barre de défilement
        tree_frame = tb.Frame(self.bus_tab, bootstyle="light")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.bus_tree = self.create_treeview(tree_frame, ["id_bus", "bus_number", "capacity"], "bus")
        self.bus_tree.pack(fill="both", expand=True)
    
    def create_treeview(self, parent, columns, bootstyle_name):
        style = ttk.Style()
        style.configure(f"{bootstyle_name}.Treeview.Heading", font=("Arial", 10, "bold"))
        
        tree = tb.Treeview(parent, columns=columns, show="headings", bootstyle=bootstyle_name)
        
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=120, anchor="center")
        
        scroll_y = tb.Scrollbar(parent, orient="vertical", command=tree.yview, bootstyle="secondary-round")
        scroll_x = tb.Scrollbar(parent, orient="horizontal", command=tree.xview, bootstyle="secondary-round")
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        scroll_y.pack(side=tb.RIGHT, fill=tb.Y)
        scroll_x.pack(side=tb.BOTTOM, fill=tb.X)
        
        return tree
    
    def filter_bus_data(self, event=None):
        search_query = self.bus_search_entry.get().strip().lower()
        
        for item in self.bus_tree.get_children():
            self.bus_tree.delete(item)

        self.cur.execute("SELECT * FROM bus")
        all_rows = self.cur.fetchall()
        
        for row in all_rows:
            if search_query in str(row).lower():
                self.bus_tree.insert("", END, values=row)

    def display_all_buses(self):
        self.bus_search_entry.delete(0, END) # Effacer le champ de recherche
        for item in self.bus_tree.get_children():
            self.bus_tree.delete(item)
        self.cur.execute("SELECT * FROM bus")
        for row in self.cur.fetchall():
            self.bus_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de tous les bus terminé")

    def add_bus_window(self):
        win = tb.Toplevel(self.root, title="Ajouter un bus", resizable=(False, False), size=(400, 200))
        
        main_frame = tb.Frame(win, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        tb.Label(main_frame, text="Numéro du bus:", bootstyle="secondary").grid(row=0, column=0, pady=5, sticky="e")
        bus_number_entry = tb.Entry(main_frame, bootstyle="info")
        bus_number_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        tb.Label(main_frame, text="Capacité:", bootstyle="secondary").grid(row=1, column=0, pady=5, sticky="e")
        capacity_entry = tb.Entry(main_frame, bootstyle="info")
        capacity_entry.grid(row=1, column=1, pady=5, padx=5, sticky="we")
    
        def save():
            try:
                bus_number = bus_number_entry.get()
                capacity = int(capacity_entry.get())
                if not bus_number:
                    raise ValueError("Le numéro du bus ne peut pas être vide.")
                self.cur.execute(
                    "INSERT INTO bus (bus_number, capacity) VALUES (%s, %s)",
                    (bus_number, capacity)
                )
                self.conn.commit()
                win.destroy()
                self.display_all_buses()
                tb.dialogs.Messagebox.show_info("Bus ajouté avec succès", "Succès")
                self.status_bar.config(text="Nouveau bus ajouté avec succès")
            except ValueError as ve:
                tb.dialogs.Messagebox.show_error(str(ve), "Erreur de saisie")
            except Exception as e:
                tb.dialogs.Messagebox.show_error(str(e), "Erreur")
                self.status_bar.config(text="Erreur lors de l'ajout du bus")

        button_frame = tb.Frame(main_frame)
        button_frame.grid(row=2, columnspan=2, pady=15)
        
        tb.Button(button_frame, text="Enregistrer", command=save, bootstyle="success").pack(side=tb.LEFT, padx=10)
        tb.Button(button_frame, text="Annuler", command=win.destroy, bootstyle="secondary").pack(side=tb.LEFT, padx=10)

    def edit_selected_bus(self):
        selected = self.bus_tree.selection()
        if not selected:
            tb.dialogs.Messagebox.show_warning("Veuillez sélectionner un bus à modifier", "Avertissement")
            return
        
        item_values = self.bus_tree.item(selected[0])['values']
        bus_id = item_values[0]
        bus_number_old = item_values[1]
        capacity_old = item_values[2]
        
        win = tb.Toplevel(self.root, title=f"Modifier le bus ID {bus_id}", resizable=(False, False), size=(400, 200))
        
        main_frame = tb.Frame(win, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        tb.Label(main_frame, text="Numéro du bus:", bootstyle="secondary").grid(row=0, column=0, pady=5, sticky="e")
        bus_number_entry = tb.Entry(main_frame, bootstyle="info")
        bus_number_entry.insert(0, bus_number_old)
        bus_number_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        tb.Label(main_frame, text="Capacité:", bootstyle="secondary").grid(row=1, column=0, pady=5, sticky="e")
        capacity_entry = tb.Entry(main_frame, bootstyle="info")
        capacity_entry.insert(0, capacity_old)
        capacity_entry.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        
        def save_changes():
            try:
                bus_number = bus_number_entry.get()
                capacity = int(capacity_entry.get())
                if not bus_number:
                    raise ValueError("Le numéro du bus ne peut pas être vide.")
                self.cur.execute(
                    "UPDATE bus SET bus_number = %s, capacity = %s WHERE id_bus = %s",
                    (bus_number, capacity, bus_id)
                )
                self.conn.commit()
                win.destroy()
                self.display_all_buses()
                tb.dialogs.Messagebox.show_info(f"Bus ID {bus_id} mis à jour avec succès", "Succès")
                self.status_bar.config(text=f"Bus ID {bus_id} mis à jour avec succès")
            except ValueError as ve:
                tb.dialogs.Messagebox.show_error(str(ve), "Erreur de saisie")
            except Exception as e:
                tb.dialogs.Messagebox.show_error(str(e), "Erreur")
                self.status_bar.config(text="Erreur lors de la mise à jour du bus")

        button_frame = tb.Frame(main_frame)
        button_frame.grid(row=2, columnspan=2, pady=15)
        
        tb.Button(button_frame, text="Enregistrer", command=save_changes, bootstyle="success").pack(side=tb.LEFT, padx=10)
        tb.Button(button_frame, text="Annuler", command=win.destroy, bootstyle="secondary").pack(side=tb.LEFT, padx=10)

    def delete_selected_bus(self):
        selected = self.bus_tree.selection()
        if not selected:
            tb.dialogs.Messagebox.show_warning("Veuillez sélectionner un bus à supprimer", "Avertissement")
            self.status_bar.config(text="Aucun bus sélectionné pour la suppression")
            return
        
        bus_id = self.bus_tree.item(selected[0])['values'][0]
        if tb.dialogs.Messagebox.okcancel(f"Voulez-vous vraiment supprimer le bus avec ID {bus_id} ?", "Confirmation"):
            try:
                self.cur.execute("DELETE FROM bus WHERE id_bus = %s", (bus_id,))
                self.conn.commit()
                self.display_all_buses()
                tb.dialogs.Messagebox.show_info("Bus supprimé avec succès", "Succès")
                self.status_bar.config(text=f"Bus ID {bus_id} supprimé avec succès")
            except Exception as e:
                tb.dialogs.Messagebox.show_error(str(e), "Erreur")
                self.status_bar.config(text="Erreur lors de la suppression du bus")

    # --- Widgets pour la gestion des Lignes ---
    def create_lines_widgets(self):
        control_frame = tb.Frame(self.lines_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)

        search_frame = tb.Frame(control_frame, bootstyle="light")
        search_frame.pack(side=tb.LEFT, padx=5, pady=5)
        tb.Label(search_frame, text="Rechercher:", bootstyle="secondary").pack(side=tb.LEFT)
        self.lines_search_entry = tb.Entry(search_frame, bootstyle="info")
        self.lines_search_entry.pack(side=tb.LEFT, padx=5)
        self.lines_search_entry.bind("<KeyRelease>", self.filter_lines_data)
        
        button_frame = tb.Frame(control_frame, bootstyle="light")
        button_frame.pack(side=tb.RIGHT, padx=5, pady=5)
        tb.Button(button_frame, text="Afficher", command=self.display_all_lines, bootstyle="primary").pack(side=tb.LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_selected_line, bootstyle="danger").pack(side=tb.LEFT, padx=5)

        tree_frame = tb.Frame(self.lines_tab, bootstyle="light")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
        columns = ("id_line", "line_number", "line_name", "origin", "destination", "distance_km")
        self.lines_tree = self.create_treeview(tree_frame, columns, "lines")
        self.lines_tree.pack(fill="both", expand=True)

    def filter_lines_data(self, event=None):
        search_query = self.lines_search_entry.get().strip().lower()
        
        for item in self.lines_tree.get_children():
            self.lines_tree.delete(item)

        self.cur.execute("SELECT * FROM bus_line")
        all_rows = self.cur.fetchall()
        
        for row in all_rows:
            if search_query in str(row).lower():
                self.lines_tree.insert("", END, values=row)

    def display_all_lines(self):
        self.lines_search_entry.delete(0, END)
        for item in self.lines_tree.get_children():
            self.lines_tree.delete(item)
        self.cur.execute("SELECT * FROM bus_line")
        for row in self.cur.fetchall():
            self.lines_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de toutes les lignes terminé")

    def delete_selected_line(self):
        selected = self.lines_tree.selection()
        if not selected:
            tb.dialogs.Messagebox.show_warning("Veuillez sélectionner une ligne à supprimer", "Avertissement")
            self.status_bar.config(text="Aucune ligne sélectionnée pour la suppression")
            return
        line_id = self.lines_tree.item(selected[0])['values'][0]
        if tb.dialogs.Messagebox.okcancel(f"Voulez-vous vraiment supprimer la ligne avec ID {line_id} ?", "Confirmation"):
            try:
                self.cur.execute("DELETE FROM bus_line WHERE id_line = %s", (line_id,))
                self.conn.commit()
                self.display_all_lines()
                tb.dialogs.Messagebox.show_info("Ligne supprimée avec succès", "Succès")
                self.status_bar.config(text=f"Ligne ID {line_id} supprimée avec succès")
            except Exception as e:
                tb.dialogs.Messagebox.show_error(str(e), "Erreur")
                self.status_bar.config(text="Erreur lors de la suppression de la ligne")

    # --- Widgets pour la gestion des Arrêts ---
    def create_stops_widgets(self):
        control_frame = tb.Frame(self.stops_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)

        search_frame = tb.Frame(control_frame, bootstyle="light")
        search_frame.pack(side=tb.LEFT, padx=5, pady=5)
        tb.Label(search_frame, text="Rechercher:", bootstyle="secondary").pack(side=tb.LEFT)
        self.stops_search_entry = tb.Entry(search_frame, bootstyle="info")
        self.stops_search_entry.pack(side=tb.LEFT, padx=5)
        self.stops_search_entry.bind("<KeyRelease>", self.filter_stops_data)

        button_frame = tb.Frame(control_frame, bootstyle="light")
        button_frame.pack(side=tb.RIGHT, padx=5, pady=5)
        tb.Button(button_frame, text="Afficher", command=self.display_all_stops, bootstyle="primary").pack(side=tb.LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_selected_stop, bootstyle="danger").pack(side=tb.LEFT, padx=5)

        tree_frame = tb.Frame(self.stops_tab, bootstyle="light")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("id_stop", "stop_name", "latitude", "longitude", "zone")
        self.stops_tree = self.create_treeview(tree_frame, columns, "stops")
        self.stops_tree.pack(fill="both", expand=True)

    def filter_stops_data(self, event=None):
        search_query = self.stops_search_entry.get().strip().lower()
        
        for item in self.stops_tree.get_children():
            self.stops_tree.delete(item)

        self.cur.execute("SELECT * FROM stop")
        all_rows = self.cur.fetchall()
        
        for row in all_rows:
            if search_query in str(row).lower():
                self.stops_tree.insert("", END, values=row)

    def display_all_stops(self):
        self.stops_search_entry.delete(0, END)
        for item in self.stops_tree.get_children():
            self.stops_tree.delete(item)
        self.cur.execute("SELECT * FROM stop")
        for row in self.cur.fetchall():
            self.stops_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de tous les arrêts terminé")

    def delete_selected_stop(self):
        selected = self.stops_tree.selection()
        if not selected:
            tb.dialogs.Messagebox.show_warning("Veuillez sélectionner un arrêt à supprimer", "Avertissement")
            self.status_bar.config(text="Aucun arrêt sélectionné pour la suppression")
            return
        stop_id = self.stops_tree.item(selected[0])['values'][0]
        if tb.dialogs.Messagebox.okcancel(f"Voulez-vous vraiment supprimer l'arrêt avec ID {stop_id} ?", "Confirmation"):
            try:
                self.cur.execute("DELETE FROM stop WHERE id_stop = %s", (stop_id,))
                self.conn.commit()
                self.display_all_stops()
                tb.dialogs.Messagebox.show_info("Arrêt supprimé avec succès", "Succès")
                self.status_bar.config(text=f"Arrêt ID {stop_id} supprimé avec succès")
            except Exception as e:
                tb.dialogs.Messagebox.show_error(str(e), "Erreur")
                self.status_bar.config(text="Erreur lors de la suppression de l'arrêt")

    # --- Widgets pour la gestion des Trajets ---
    def create_trips_widgets(self):
        control_frame = tb.Frame(self.trips_tab, bootstyle="light")
        control_frame.pack(fill="x", padx=15, pady=10)

        search_frame = tb.Frame(control_frame, bootstyle="light")
        search_frame.pack(side=tb.LEFT, padx=5, pady=5)
        tb.Label(search_frame, text="Rechercher:", bootstyle="secondary").pack(side=tb.LEFT)
        self.trips_search_entry = tb.Entry(search_frame, bootstyle="info")
        self.trips_search_entry.pack(side=tb.LEFT, padx=5)
        self.trips_search_entry.bind("<KeyRelease>", self.filter_trips_data)

        button_frame = tb.Frame(control_frame, bootstyle="light")
        button_frame.pack(side=tb.RIGHT, padx=5, pady=5)
        tb.Button(button_frame, text="Afficher", command=self.display_all_trips, bootstyle="primary").pack(side=tb.LEFT, padx=5)
        tb.Button(button_frame, text="Supprimer", command=self.delete_selected_trip, bootstyle="danger").pack(side=tb.LEFT, padx=5)

        tree_frame = tb.Frame(self.trips_tab, bootstyle="light")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("id_trip", "line_number", "driver_name", "start_datetime", "end_datetime", "status")
        self.trips_tree = self.create_treeview(tree_frame, columns, "trips")
        self.trips_tree.pack(fill="both", expand=True)
    
    def filter_trips_data(self, event=None):
        search_query = self.trips_search_entry.get().strip().lower()
        
        for item in self.trips_tree.get_children():
            self.trips_tree.delete(item)

        self.cur.execute("SELECT id_trip, line_number, driver_name, start_datetime, end_datetime, status FROM trip")
        all_rows = self.cur.fetchall()
        
        for row in all_rows:
            if search_query in str(row).lower():
                self.trips_tree.insert("", END, values=row)

    def display_all_trips(self):
        self.trips_search_entry.delete(0, END)
        for item in self.trips_tree.get_children():
            self.trips_tree.delete(item)
        self.cur.execute("SELECT id_trip, line_number, driver_name, start_datetime, end_datetime, status FROM trip")
        for row in self.cur.fetchall():
            self.trips_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de tous les trajets terminé")

    def delete_selected_trip(self):
        selected = self.trips_tree.selection()
        if not selected:
            tb.dialogs.Messagebox.show_warning("Veuillez sélectionner un trajet à supprimer", "Avertissement")
            self.status_bar.config(text="Aucun trajet sélectionné pour la suppression")
            return
        trip_id = self.trips_tree.item(selected[0])['values'][0]
        if tb.dialogs.Messagebox.okcancel(f"Voulez-vous vraiment supprimer le trajet avec ID {trip_id} ?", "Confirmation"):
            try:
                self.cur.execute("DELETE FROM trip WHERE id_trip = %s", (trip_id,))
                self.conn.commit()
                self.display_all_trips()
                tb.dialogs.Messagebox.show_info("Trajet supprimé avec succès", "Succès")
                self.status_bar.config(text=f"Trajet ID {trip_id} supprimé avec succès")
            except Exception as e:
                tb.dialogs.Messagebox.show_error(str(e), "Erreur")
                self.status_bar.config(text="Erreur lors de la suppression du trajet")

    # --- Widgets pour les Statistiques ---
    def create_stats_widgets(self):
        main_frame = tb.Frame(self.stats_tab, bootstyle="light")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
    
        selection_frame = tb.LabelFrame(main_frame, text="Sélection de la Ligne", bootstyle="secondary")
        selection_frame.pack(fill="x", pady=(0, 15), ipady=5)

        tb.Label(selection_frame, text="Sélectionnez une ligne:", bootstyle="secondary").pack(side=tb.LEFT, padx=5, pady=10)
    
        self.line_var = StringVar()
        self.cur.execute("SELECT line_number, line_name FROM bus_line")
        lines = self.cur.fetchall()
        line_options = [f"{line[0]} - {line[1]}" for line in lines]
        
        self.line_combobox = tb.Combobox(selection_frame, textvariable=self.line_var, values=line_options, bootstyle="info", width=40, state="readonly")
        self.line_combobox.pack(side=tb.LEFT, padx=5, pady=10)
        
        tb.Button(selection_frame, text="Afficher les statistiques", command=self.show_line_stats, bootstyle="primary").pack(side=tb.LEFT, padx=5, pady=10)
    
        result_frame = tb.LabelFrame(main_frame, text="Résultats Statistiques", bootstyle="secondary")
        result_frame.pack(fill="both", expand=True)

        self.stats_text = tb.Text(result_frame, height=15, wrap="word")
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)

    def show_line_stats(self):
        line_selection = self.line_var.get()
        if not line_selection:
            tb.dialogs.Messagebox.show_warning("Veuillez sélectionner une ligne.", "Avertissement")
            return
            
        line_number = line_selection.split(" - ")[0]
        self.cur.execute("SELECT COUNT(*), AVG(distance_km) FROM trip WHERE line_number = %s", (line_number,))
        stats = self.cur.fetchone()
        
        self.cur.execute("SELECT COUNT(DISTINCT driver_name) FROM trip WHERE line_number = %s", (line_number,))
        driver_count = self.cur.fetchone()[0]

        self.stats_text.delete(1.0, END)
        self.stats_text.insert(END, f"Statistiques pour la ligne {line_number} :\n\n")
        self.stats_text.insert(END, f"Nombre total de trajets : {stats[0]}\n")
        self.stats_text.insert(END, f"Distance moyenne par trajet : {stats[1]:.2f} km\n")
        self.stats_text.insert(END, f"Nombre de conducteurs différents : {driver_count}\n")
        self.status_bar.config(text=f"Statistiques affichées pour la ligne {line_number}")

    def __del__(self):
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    app = tb.Window(themename="yeti")
    BusManagementApp(app)
    app.mainloop()