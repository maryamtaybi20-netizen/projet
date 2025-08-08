import psycopg2
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.font import Font


class BusManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion du Trafic des Bus - Système de Transport")
        self.root.geometry("1280x720")
        self.root.configure(bg="#f5f5f5")
        
        # Définition des polices
        self.title_font = Font(family="Helvetica", size=12, weight="bold")
        self.button_font = Font(family="Arial", size=10)
        self.tree_font = Font(family="Arial", size=9)

        # Connexion à la base de données
        self.conn = psycopg2.connect(
            dbname="bus_traffic_stats",
            user="postgres",
            password="2006",
            host="localhost",
            port="5432"
        )
        self.cur = self.conn.cursor()

         
        style = ttk.Style()
        style.theme_use("clam")
    

        # Configuration des couleurs et polices pour les Treeviews et les boutons
        self.tree_colors = {
            "bus": {"bg": "#e3f2fd", "fg": "#7694c2", "heading_bg": "#1565c0", "heading_fg": "white"},
            "lines": {"bg": "#e8f5e9", "fg": "#2e7d32", "heading_bg": "#388e3c", "heading_fg": "white"},
            "stops": {"bg": "#fff3e0", "fg": "#e65100", "heading_bg": "#fb8c00", "heading_fg": "white"},
            "trips": {"bg": "#f3e5f5", "fg": "#6a1b9a", "heading_bg": "#8e24aa", "heading_fg": "white"},
            "stats": {"bg": "#e1f5fe", "fg": "#0277bd", "heading_bg": "#0288d1", "heading_fg": "white"}
        }

        
        for table, colors in self.tree_colors.items():
            style.configure(f"{table}.Treeview",
                          background=colors["bg"],
                          foreground=colors["fg"],
                          rowheight=28,
                          fieldbackground=colors["bg"],
                          font=self.tree_font)
            style.map(f"{table}.Treeview", background=[('selected', colors["heading_bg"])])
            
            style.configure(f"{table}.Treeview.Heading",
                          background=colors["heading_bg"],
                          foreground=colors["heading_fg"],
                          font=('Arial', 10, 'bold'),
                          padding=5)
        
       
        style.configure("TButton",
                      font=self.button_font,
                      padding=6,
                      relief="flat",
                      background="#2c7be5",
                      foreground="white")
        style.map("TButton",
                 background=[('active', '#1a68cc'), ('disabled', '#cccccc')])

         
        title_frame = Frame(root, bg="#2c7be5", height=60)
        title_frame.pack(fill="x")
        Label(title_frame, text="SYSTÈME DE GESTION DU TRAFIC DES BUS", 
              font=("Helvetica", 16, "bold"), bg="#2c7be5", fg="white").pack(pady=15)

        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=(0,10), padx=10, expand=True, fill="both")

        self.bus_tab = Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.bus_tab, text="Gestion des Bus")
        self.create_bus_widgets()

        self.lines_tab = Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.lines_tab, text="Gestion des Lignes")
        self.create_lines_widgets()

        self.stops_tab = Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.stops_tab, text="Gestion des Arrêts")
        self.create_stops_widgets()

        self.trips_tab = Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.trips_tab, text="Gestion des Trajets")
        self.create_trips_widgets()

        self.stats_tab = Frame(self.notebook, bg="#ffffff")
        self.notebook.add(self.stats_tab, text="Statistiques et Rapports")
        self.create_stats_widgets()

        
        self.status_bar = Label(root, text="Prêt", bd=1, relief=SUNKEN, anchor=W, 
                               bg="#e9ecef", fg="#333", font=("Arial", 9))
        self.status_bar.pack(fill="x", padx=10, pady=(0,5))

    def create_bus_widgets(self):
        control_frame = LabelFrame(self.bus_tab, text="Contrôles des Bus", bg="#ffffff", 
                                 font=self.title_font, bd=2, relief=GROOVE)
        control_frame.pack(fill="x", padx=15, pady=10, ipady=5)

        ttk.Button(control_frame, text="Afficher tous les bus", command=self.display_all_buses, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Ajouter un bus", command=self.add_bus_window, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Supprimer le bus sélectionné", command=self.delete_selected_bus, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)

        # إطار Treeview مع شريط تمرير
        tree_frame = Frame(self.bus_tab, bg="#ffffff")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ("id_bus", "bus_number", "capacity")
        self.bus_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                    yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                    style="bus.Treeview")
        
        # تحسين عرض الأعمدة
        col_widths = {"id_bus": 80, "bus_number": 120, "capacity": 100}
        for col in columns:
            self.bus_tree.heading(col, text=col.replace("_", " ").title())
            self.bus_tree.column(col, width=col_widths.get(col, 120), anchor="center")
        
        scroll_y.config(command=self.bus_tree.yview)
        scroll_x.config(command=self.bus_tree.xview)

        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.bus_tree.pack(fill="both", expand=True)

    def display_all_buses(self):
        for item in self.bus_tree.get_children():
            self.bus_tree.delete(item)
        self.cur.execute("SELECT * FROM bus")
        for row in self.cur.fetchall():
            self.bus_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de tous les bus terminé")

    def add_bus_window(self):
        win = Toplevel(self.root)
        win.title("Ajouter un bus")
        win.geometry("400x200")
        win.resizable(False, False)
        
        main_frame = Frame(win, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        Label(main_frame, text="Numéro du bus:", bg="#ffffff", font=self.button_font).grid(row=0, column=0, pady=5, sticky="e")
        bus_number_entry = Entry(main_frame, font=self.button_font)
        bus_number_entry.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        Label(main_frame, text="Capacité:", bg="#ffffff", font=self.button_font).grid(row=1, column=0, pady=5, sticky="e")
        capacity_entry = Entry(main_frame, font=self.button_font)
        capacity_entry.grid(row=1, column=1, pady=5, padx=5, sticky="we")
 
        button_frame = Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=2, columnspan=2, pady=15)
        
        def save():
            try:
                self.cur.execute(
                    "INSERT INTO bus (bus_number, capacity) VALUES (%s, %s)",
                    (bus_number_entry.get(), capacity_entry.get())
                )
                self.conn.commit()
                win.destroy()
                self.display_all_buses()
                messagebox.showinfo("Succès", "Bus ajouté avec succès")
                self.status_bar.config(text="Nouveau bus ajouté avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                self.status_bar.config(text="Erreur lors de l'ajout du bus")

        ttk.Button(button_frame, text="Enregistrer", command=save, style="TButton").pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="Annuler", command=win.destroy, style="TButton").pack(side=LEFT, padx=10)

    def delete_selected_bus(self):
        selected = self.bus_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un bus à supprimer")
            self.status_bar.config(text="Aucun bus sélectionné pour la suppression")
            return
        bus_id = self.bus_tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le bus avec ID {bus_id} ?")
        if confirm:
            try:
                self.cur.execute("DELETE FROM bus WHERE id_bus = %s", (bus_id,))
                self.conn.commit()
                self.display_all_buses()
                messagebox.showinfo("Succès", "Bus supprimé avec succès")
                self.status_bar.config(text=f"Bus ID {bus_id} supprimé avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                self.status_bar.config(text="Erreur lors de la suppression du bus")

    def create_lines_widgets(self):
        control_frame = LabelFrame(self.lines_tab, text="Contrôles des Lignes", bg="#ffffff", 
                                 font=self.title_font, bd=2, relief=GROOVE)
        control_frame.pack(fill="x", padx=15, pady=10, ipady=5)

        ttk.Button(control_frame, text="Afficher toutes les lignes", command=self.display_all_lines, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Supprimer la ligne sélectionnée", command=self.delete_selected_line, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)

        tree_frame = Frame(self.lines_tab, bg="#ffffff")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
 
        columns = ("id_line", "line_number", "line_name", "origin", "destination", "distance_km")
        self.lines_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                     yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                     style="lines.Treeview")
        
        col_widths = {"id_line": 80, "line_number": 100, "line_name": 150, 
                     "origin": 120, "destination": 120, "distance_km": 100}
        for col in columns:
            self.lines_tree.heading(col, text=col.replace("_", " ").title())
            self.lines_tree.column(col, width=col_widths.get(col, 120), anchor="center")
        
        scroll_y.config(command=self.lines_tree.yview)
        scroll_x.config(command=self.lines_tree.xview)

        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.lines_tree.pack(fill="both", expand=True)

    def display_all_lines(self):
        for item in self.lines_tree.get_children():
            self.lines_tree.delete(item)
        self.cur.execute("SELECT * FROM bus_line")
        for row in self.cur.fetchall():
            self.lines_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de toutes les lignes terminé")

    def delete_selected_line(self):
        selected = self.lines_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne à supprimer")
            self.status_bar.config(text="Aucune ligne sélectionnée pour la suppression")
            return
        line_id = self.lines_tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer la ligne avec ID {line_id} ?")
        if confirm:
            try:
                self.cur.execute("DELETE FROM bus_line WHERE id_line = %s", (line_id,))
                self.conn.commit()
                self.display_all_lines()
                messagebox.showinfo("Succès", "Ligne supprimée avec succès")
                self.status_bar.config(text=f"Ligne ID {line_id} supprimée avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                self.status_bar.config(text="Erreur lors de la suppression de la ligne")

    def create_stops_widgets(self):
        control_frame = LabelFrame(self.stops_tab, text="Contrôles des Arrêts", bg="#ffffff", 
                                 font=self.title_font, bd=2, relief=GROOVE)
        control_frame.pack(fill="x", padx=15, pady=10, ipady=5)

        ttk.Button(control_frame, text="Afficher tous les arrêts", command=self.display_all_stops, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Supprimer l'arrêt sélectionné", command=self.delete_selected_stop, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)

        tree_frame = Frame(self.stops_tab, bg="#ffffff")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ("id_stop", "stop_name", "latitude", "longitude", "zone")
        self.stops_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                      yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                      style="stops.Treeview")
        
        col_widths = {"id_stop": 80, "stop_name": 180, "latitude": 120, 
                     "longitude": 120, "zone": 100}
        for col in columns:
            self.stops_tree.heading(col, text=col.replace("_", " ").title())
            self.stops_tree.column(col, width=col_widths.get(col, 120), anchor="center")
        
        scroll_y.config(command=self.stops_tree.yview)
        scroll_x.config(command=self.stops_tree.xview)

        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.stops_tree.pack(fill="both", expand=True)

    def display_all_stops(self):
        for item in self.stops_tree.get_children():
            self.stops_tree.delete(item)
        self.cur.execute("SELECT * FROM stop")
        for row in self.cur.fetchall():
            self.stops_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de tous les arrêts terminé")

    def delete_selected_stop(self):
        selected = self.stops_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un arrêt à supprimer")
            self.status_bar.config(text="Aucun arrêt sélectionné pour la suppression")
            return
        stop_id = self.stops_tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer l'arrêt avec ID {stop_id} ?")
        if confirm:
            try:
                self.cur.execute("DELETE FROM stop WHERE id_stop = %s", (stop_id,))
                self.conn.commit()
                self.display_all_stops()
                messagebox.showinfo("Succès", "Arrêt supprimé avec succès")
                self.status_bar.config(text=f"Arrêt ID {stop_id} supprimé avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                self.status_bar.config(text="Erreur lors de la suppression de l'arrêt")

    def create_trips_widgets(self):
        control_frame = LabelFrame(self.trips_tab, text="Contrôles des Trajets", bg="#ffffff", 
                                 font=self.title_font, bd=2, relief=GROOVE)
        control_frame.pack(fill="x", padx=15, pady=10, ipady=5)

        ttk.Button(control_frame, text="Afficher tous les trajets", command=self.display_all_trips, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Supprimer le trajet sélectionné", command=self.delete_selected_trip, 
                  style="TButton").pack(side=LEFT, padx=5, pady=5)

        tree_frame = Frame(self.trips_tab, bg="#ffffff")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ("id_trip", "line_number", "driver_name", "start_datetime", "end_datetime", "status")
        self.trips_tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                     yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                     style="trips.Treeview")
        
        col_widths = {"id_trip": 80, "line_number": 100, "driver_name": 150, 
                     "start_datetime": 160, "end_datetime": 160, "status": 100}
        for col in columns:
            self.trips_tree.heading(col, text=col.replace("_", " ").title())
            self.trips_tree.column(col, width=col_widths.get(col, 120), anchor="center")
        
        scroll_y.config(command=self.trips_tree.yview)
        scroll_x.config(command=self.trips_tree.xview)

        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.pack(side=BOTTOM, fill=X)
        self.trips_tree.pack(fill="both", expand=True)

    def display_all_trips(self):
        for item in self.trips_tree.get_children():
            self.trips_tree.delete(item)
        self.cur.execute("SELECT id_trip, line_number, driver_name, start_datetime, end_datetime, status FROM trip")
        for row in self.cur.fetchall():
            self.trips_tree.insert("", END, values=row)
        self.status_bar.config(text="Affichage de tous les trajets terminé")

    def delete_selected_trip(self):
        selected = self.trips_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un trajet à supprimer")
            self.status_bar.config(text="Aucun trajet sélectionné pour la suppression")
            return
        trip_id = self.trips_tree.item(selected[0])['values'][0]
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le trajet avec ID {trip_id} ?")
        if confirm:
            try:
                self.cur.execute("DELETE FROM trip WHERE id_trip = %s", (trip_id,))
                self.conn.commit()
                self.display_all_trips()
                messagebox.showinfo("Succès", "Trajet supprimé avec succès")
                self.status_bar.config(text=f"Trajet ID {trip_id} supprimé avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                self.status_bar.config(text="Erreur lors de la suppression du trajet")

    def create_stats_widgets(self):
        main_frame = Frame(self.stats_tab, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
 
        selection_frame = LabelFrame(main_frame, text="Sélection de la Ligne", bg="#ffffff", 
                                   font=self.title_font, bd=2, relief=GROOVE)
        selection_frame.pack(fill="x", pady=(0,15))

        Label(selection_frame, text="Sélectionnez une ligne:", bg="#ffffff", 
             font=self.button_font).pack(side=LEFT, padx=5, pady=10)
        
        self.line_var = StringVar()
        self.cur.execute("SELECT line_number, line_name FROM bus_line")
        lines = self.cur.fetchall()
        line_options = [f"{line[0]} - {line[1]}" for line in lines]
        
        self.line_combobox = ttk.Combobox(selection_frame, textvariable=self.line_var, 
                                         values=line_options, font=self.button_font, width=40)
        self.line_combobox.pack(side=LEFT, padx=5, pady=10)
        
        ttk.Button(selection_frame, text="Afficher les statistiques", command=self.show_line_stats, 
                  style="TButton").pack(side=LEFT, padx=5, pady=10)
 
        result_frame = LabelFrame(main_frame, text="Résultats Statistiques", bg="#ffffff", 
                                font=self.title_font, bd=2, relief=GROOVE)
        result_frame.pack(fill="both", expand=True)

        self.stats_text = Text(result_frame, height=15, wrap=WORD, bg="white", 
                             font=("Arial", 10), padx=10, pady=10)
        scroll_y = ttk.Scrollbar(result_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=scroll_y.set)
        
        scroll_y.pack(side=RIGHT, fill=Y)
        self.stats_text.pack(fill="both", expand=True, padx=5, pady=5)

    def show_line_stats(self):
        line_number = self.line_var.get().split(" - ")[0]
        self.cur.execute("SELECT COUNT(*), AVG(distance_km), COUNT(DISTINCT driver_name) FROM trip WHERE line_number = %s", (line_number,))
        stats = self.cur.fetchone()

        self.stats_text.delete(1.0, END)
        self.stats_text.insert(END, f"Statistiques pour la ligne {line_number} :\n")
        self.stats_text.insert(END, f"Nombre de trajets : {stats[0]}\n")
        self.stats_text.insert(END, f"Distance moyenne : {stats[1]:.2f} km\n")
        self.stats_text.insert(END, f"Nombre de conducteurs : {stats[2]}\n")
        self.status_bar.config(text=f"Statistiques affichées pour la ligne {line_number}")

    def __del__(self):
        if hasattr(self, 'cur'):
            self.cur.close()
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = BusManagementApp(root)
    root.mainloop()