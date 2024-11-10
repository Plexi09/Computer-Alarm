import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import time
import sys
import os
import logging
from pygame import mixer
from datetime import datetime
import threading
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.toast import ToastNotification
import customtkinter as ctk

class SecurityMonitorGUI:
    def __init__(self):
        self.setup_system()
        self.create_window()
        self.create_gui()
        self.setup_charts()

    def setup_system(self):
        """Initialisation du système"""
        # Configuration des logs
        log_dir = os.path.join(os.path.expanduser("~"), ".security_logs")
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"security_{datetime.now().strftime('%Y%m%d')}.log")
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # Initialisation audio
        mixer.init()

        # Variables d'état
        self.monitoring_active = False
        self.alert_active = False
        self.incident_count = 0
        self.system_metrics = []
        self.last_check = datetime.now()

    def create_window(self):
        """Création de la fenêtre principale avec thème moderne"""
        self.root = ttk.Window(
            title="Système de Surveillance Pro",
            themename="darkly",
            size=(1024, 768),
            resizable=(True, True)
        )
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configuration de la grille principale
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

    def create_gui(self):
        """Interface utilisateur modernisée"""
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

    def create_header(self):
        """En-tête amélioré avec barre de navigation"""
        header = ttk.Frame(self.root, style='primary.TFrame', padding=10)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Logo et titre
        title_frame = ttk.Frame(header)
        title_frame.pack(side="left")

        title = ttk.Label(
            title_frame,
            text="🛡️ Security Monitor Pro",
            font=("Helvetica", 20, "bold"),
            style='primary.Inverse.TLabel'
        )
        title.pack(side="left", padx=10)

        # Indicateurs d'état
        status_frame = ttk.Frame(header)
        status_frame.pack(side="right")

        self.cpu_label = ttk.Label(
            status_frame,
            text="CPU: 0%",
            style='primary.Inverse.TLabel'
        )
        self.cpu_label.pack(side="left", padx=10)

        self.memory_label = ttk.Label(
            status_frame,
            text="RAM: 0%",
            style='primary.Inverse.TLabel'
        )
        self.memory_label.pack(side="left", padx=10)

        self.status_label = ttk.Label(
            status_frame,
            text="■ Système Inactif",
            style='primary.Inverse.TLabel'
        )
        self.status_label.pack(side="left", padx=10)

    def create_sidebar(self):
        """Panneau de contrôle latéral"""
        sidebar = ttk.Frame(self.root, style='secondary.TFrame', padding=10)
        sidebar.grid(row=1, column=0, sticky="nsew")

        # Contrôles principaux
        controls = ttk.LabelFrame(sidebar, text="Contrôles", padding=10)
        controls.pack(fill="x", pady=5)

        self.start_button = ttk.Button(
            controls,
            text="▶ Démarrer la surveillance",
            command=self.toggle_monitoring,
            style='success.TButton',
            width=25
        )
        self.start_button.pack(pady=5, fill="x")

        self.stop_alert_button = ttk.Button(
            controls,
            text="🔕 Désactiver l'alerte",
            command=self.stop_alert,
            style='danger.TButton',
            state="disabled",
            width=25
        )
        self.stop_alert_button.pack(pady=5, fill="x")

        # Statistiques
        stats = ttk.LabelFrame(sidebar, text="Statistiques", padding=10)
        stats.pack(fill="x", pady=5)

        self.incident_label = ttk.Label(
            stats,
            text="🚨 Incidents: 0",
            style='primary.TLabel'
        )
        self.incident_label.pack(pady=5)

        self.time_label = ttk.Label(
            stats,
            text="⏱️ Durée: 00:00:00",
            style='primary.TLabel'
        )
        self.time_label.pack(pady=5)

        # Paramètres
        settings = ttk.LabelFrame(sidebar, text="Paramètres", padding=10)
        settings.pack(fill="x", pady=5)

        ttk.Label(settings, text="Sensibilité:").pack(pady=2)
        self.sensitivity = ttk.Scale(
            settings,
            from_=1,
            to=10,
            value=5
        )
        self.sensitivity.pack(fill="x", pady=5)

        # Mode sonore
        self.sound_var = tk.BooleanVar(value=True)
        sound_check = ttk.Checkbutton(
            settings,
            text="Alerte sonore",
            variable=self.sound_var,
            style='primary.TCheckbutton'
        )
        sound_check.pack(pady=5)

    def create_main_content(self):
        """Contenu principal avec visualisations"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=1, column=1, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Métriques en temps réel
        metrics_frame = ttk.Frame(main_frame)
        metrics_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)

        # Cartes de métriques
        self.create_metric_card(metrics_frame, 0, "Tension Batterie", "12.5V")
        self.create_metric_card(metrics_frame, 1, "Charge CPU", "25%")
        self.create_metric_card(metrics_frame, 2, "Mémoire", "4.2GB")
        self.create_metric_card(metrics_frame, 3, "Température", "45°C")

        # Zone de logs améliorée
        log_frame = ttk.LabelFrame(main_frame, text="Journal de Sécurité", padding=10)
        log_frame.grid(row=1, column=0, sticky="nsew")

        # Barre d'outils des logs
        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill="x", pady=(0, 5))

        ttk.Button(
            log_toolbar,
            text="📁 Exporter",
            style='primary.Outline.TButton',
            command=self.export_logs
        ).pack(side="left", padx=5)

        ttk.Button(
            log_toolbar,
            text="🗑️ Effacer",
            style='danger.Outline.TButton',
            command=self.clear_logs
        ).pack(side="left", padx=5)

        # Zone de texte des logs
        self.log_text = tk.Text(
            log_frame,
            height=20,
            wrap=tk.WORD,
            bg='#2b3e50',
            fg='#ffffff',
            font=("Consolas", 10)
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Configuration des tags pour le formatage
        self.log_text.tag_configure("timestamp", foreground="#888888")
        self.log_text.tag_configure("info", foreground="#4CAF50")
        self.log_text.tag_configure("warning", foreground="#FFC107")
        self.log_text.tag_configure("alert", foreground="#F44336")

    def create_metric_card(self, parent, column, title, value):
        """Création d'une carte de métrique"""
        card = ttk.Frame(parent, style='primary.TFrame')
        card.grid(row=0, column=column, padx=5, sticky="ew")

        ttk.Label(
            card,
            text=title,
            style='primary.Inverse.TLabel',
            font=("Helvetica", 10)
        ).pack(pady=2)

        ttk.Label(
            card,
            text=value,
            style='primary.Inverse.TLabel',
            font=("Helvetica", 16, "bold")
        ).pack(pady=2)

    def create_status_bar(self):
        """Barre d'état avec progression"""
        status_bar = ttk.Frame(self.root, style='primary.TFrame', padding=5)
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.progress = ttk.Progressbar(
            status_bar,
            mode='indeterminate',
            style='success.Horizontal.TProgressbar'
        )
        self.progress.pack(fill="x", padx=5)

    def setup_charts(self):
        """Configuration des graphiques"""
        self.update_metrics()  # Démarrage de la mise à jour des métriques

    def update_metrics(self):
        """Mise à jour des métriques système"""
        if hasattr(self, 'root'):
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            self.cpu_label.configure(text=f"CPU: {cpu_percent}%")
            self.memory_label.configure(text=f"RAM: {memory.percent}%")

            battery = psutil.sensors_battery()
            if battery:
                self.update_metric_card(0, f"{battery.percent}%")

            self.update_metric_card(1, f"{cpu_percent}%")
            self.update_metric_card(2, f"{memory.percent}%")

            # Ajout des données pour les graphiques
            self.system_metrics.append({
                'timestamp': datetime.now(),
                'cpu': cpu_percent,
                'memory': memory.percent
            })

            # Limite la taille des données historiques
            if len(self.system_metrics) > 100:
                self.system_metrics.pop(0)

            self.root.after(1000, self.update_metrics)

    def update_metric_card(self, index, value):
        """Mise à jour d'une carte de métrique"""
        metrics_frame = self.root.grid_slaves(row=1, column=1)[0].grid_slaves(row=0, column=0)[0]
        card = metrics_frame.grid_slaves(column=index)[0]
        card.pack_slaves()[1].configure(text=value)

    def export_logs(self):
        """Exportation des logs"""
        filename = f"security_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write(self.log_text.get("1.0", tk.END))

        toast = ToastNotification(
            title="Export réussi",
            message=f"Logs exportés vers {filename}",
            duration=3000
        )
        toast.show_toast()

    def clear_logs(self):
        """Effacement des logs"""
        if Messagebox.show_question(
            "Confirmation",
            "Voulez-vous vraiment effacer tous les logs ?",
            parent=self.root
        ):
            self.log_text.delete("1.0", tk.END)
            self.log_event("Journal effacé", "info")

    def check_security(self):
        """Surveillance améliorée"""
        was_secure = True
        start_time = datetime.now()

        while self.monitoring_active:
            try:
                battery = psutil.sensors_battery()
                is_secure = battery.power_plugged if battery else True

                # Vérification supplémentaire basée sur la sensibilité
                if battery and battery.percent < (11 - self.sensitivity.get()) * 10:
                    is_secure = False

                if was_secure and not is_secure:
                    self.incident_count += 1
                    self.incident_label.configure(text=f"🚨 Incidents: {self.incident_count}")
                    self.trigger_alert("⚠️ ALERTE DE SÉCURITÉ: Alimentation compromise!")

                elif not was_secure and is_secure:
                    self.log_event("✅ Système sécurisé - Retour à la normale", "info")
                    if self.alert_active:
                        self.stop_alert()

                was_secure = is_secure

                # Mise à jour du temps de surveillance
                elapsed = datetime.now() - start_time
                self.time_label.configure(text=f"⏱️ Durée: {str(elapsed).split('.')[0]}")

                time.sleep(1)

            except Exception as e:
                self.log_event(f"Erreur de surveillance: {str(e)}", "warning")
                time.sleep(5)

    def trigger_alert(self, message):
        """Système d'alerte amélioré"""
        self.alert_active = True
        self.stop_alert_button.configure(state="normal")
        self.log_event(message, "alert")

        if self.sound_var.get():
            try:
                mixer.music.load("alarm.mp3")
                mixer.music.play(-1)
            except Exception as e:
                self.log_event(f"Erreur audio: {str(e)}", "warning")

        self.flash_warning()

        # Notification système
        ToastNotification(
            title="Alerte de Sécurité",
            message=message,
            duration=5000,
            alert=True
        ).show_toast()

    def flash_warning(self):
        """Effet visuel d'alerte amélioré"""
        if self.alert_active:
            # Alternance entre rouge et blanc pour le statut
            current_color = self.status_label.cget("foreground")
            new_color = "#F44336" if current_color != "#F44336" else "#FFFFFF"
            self.status_label.configure(foreground=new_color)

            # Met en surbrillance le fond de la fenêtre de logs
            current_bg = self.log_text.cget("background")
            new_bg = "#3B1A1A" if current_bg != "#3B1A1A" else "#2b3e50"
            self.log_text.configure(background=new_bg)

            self.root.after(500, self.flash_warning)

    def stop_alert(self):
        """Arrêt de l'alerte avec retour à la normale"""
        self.alert_active = False
        mixer.music.stop()
        self.stop_alert_button.configure(state="disabled")

        # Réinitialisation des éléments visuels
        self.status_label.configure(foreground="#FFFFFF")
        self.log_text.configure(background="#2b3e50")

        self.log_event("🔕 Alerte désactivée", "info")

        # Notification de fin d'alerte
        ToastNotification(
            title="Alerte désactivée",
            message="Le système est revenu à la normale",
            duration=3000
        ).show_toast()

    def toggle_monitoring(self):
        """Activation/désactivation de la surveillance avec animation"""
        if not self.monitoring_active:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Démarrage amélioré de la surveillance"""
        self.monitoring_active = True
        self.progress.start(10)

        # Mise à jour des éléments visuels
        self.start_button.configure(
            text="⏹️ Arrêter la surveillance",
            style='warning.TButton'
        )
        self.status_label.configure(
            text="■ Système Actif",
            foreground="#4CAF50"
        )

        # Animation de démarrage
        self.animate_startup()

        # Log et notification
        self.log_event("🟢 Système de surveillance activé", "info")
        ToastNotification(
            title="Surveillance active",
            message="Le système commence la surveillance",
            duration=3000
        ).show_toast()

        # Démarrage du thread de surveillance
        self.monitor_thread = threading.Thread(target=self.check_security)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def animate_startup(self):
        """Animation de démarrage du système"""
        def animate_progress(step=0):
            if step < 100 and self.monitoring_active:
                self.progress.configure(value=step)
                self.root.after(20, animate_progress, step + 2)
            else:
                self.progress.configure(mode='indeterminate')
                self.progress.start(10)

        self.progress.configure(mode='determinate', value=0)
        animate_progress()

    def stop_monitoring(self):
        """Arrêt contrôlé du système"""
        self.monitoring_active = False
        self.progress.stop()

        # Mise à jour des éléments visuels
        self.start_button.configure(
            text="▶ Démarrer la surveillance",
            style='success.TButton'
        )
        self.status_label.configure(
            text="■ Système Inactif",
            foreground="#FFFFFF"
        )

        # Arrêt des alertes actives
        if self.alert_active:
            self.stop_alert()

        # Log et notification
        self.log_event("🔴 Système de surveillance désactivé", "info")
        ToastNotification(
            title="Surveillance arrêtée",
            message="Le système est maintenant inactif",
            duration=3000
        ).show_toast()

    def log_event(self, message, level="info"):
        """Système de logs amélioré avec formatage et couleurs"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Configuration des styles selon le niveau
        styles = {
            "info": {"icon": "ℹ️", "color": "#4CAF50"},
            "warning": {"icon": "⚠️", "color": "#FFC107"},
            "alert": {"icon": "🚨", "color": "#F44336"}
        }

        style = styles.get(level, styles["info"])

        # Formatage du message
        formatted_message = f"{style['icon']} {message}"

        # Insertion dans l'interface avec style
        self.log_text.tag_configure(level, foreground=style['color'])
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{formatted_message}\n", level)
        self.log_text.see(tk.END)

        # Enregistrement dans le fichier
        logging.info(formatted_message)

    def on_closing(self):
        """Gestion améliorée de la fermeture"""
        if self.monitoring_active:
            response = Messagebox.show_question(
                "Confirmation",
                "Le système de surveillance est actif.\nVoulez-vous vraiment quitter ?",
                buttons=['Oui:primary', 'Non:secondary']
            )

            if response != "Oui":
                return

        # Arrêt propre du système
        self.monitoring_active = False
        if self.alert_active:
            self.stop_alert()

        # Sauvegarde des logs finaux
        self.log_event("💾 Sauvegarde et arrêt du système", "info")

        # Nettoyage
        mixer.quit()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """Lancement de l'application avec écran de démarrage"""
        # Affichage de l'écran de démarrage
        splash_window = self.show_splash_screen()

        # Initialisation en arrière-plan
        self.root.after(2000, lambda: self.finish_startup(splash_window))

        # Démarrage de la boucle principale
        self.root.mainloop()

    def show_splash_screen(self):
        """Affichage d'un écran de démarrage"""
        splash = tk.Toplevel(self.root)
        splash.title("Démarrage")
        splash.geometry("300x200")
        splash.overrideredirect(True)

        # Centrage de la fenêtre
        splash.update_idletasks()
        width = splash.winfo_width()
        height = splash.winfo_height()
        x = (splash.winfo_screenwidth() // 2) - (width // 2)
        y = (splash.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f'+{x}+{y}')

        # Contenu
        frame = ttk.Frame(splash, style='primary.TFrame')
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="🛡️",
            font=("Helvetica", 48),
            style='primary.Inverse.TLabel'
        ).pack(pady=10)

        ttk.Label(
            frame,
            text="Security Monitor Pro",
            font=("Helvetica", 16, "bold"),
            style='primary.Inverse.TLabel'
        ).pack(pady=5)

        progress = ttk.Progressbar(
            frame,
            mode='indeterminate',
            style='success.Horizontal.TProgressbar'
        )
        progress.pack(fill="x", padx=20, pady=10)
        progress.start(15)

        return splash

    def finish_startup(self, splash_window):
        """Finalisation du démarrage"""
        # Fermeture de l'écran de démarrage
        splash_window.destroy()

        # Affichage de la fenêtre principale
        self.root.deiconify()

        # Log initial
        self.log_event("🚀 Système initialisé et prêt", "info")

        # Notification de démarrage
        ToastNotification(
            title="Système Prêt",
            message="Security Monitor Pro est prêt à l'emploi",
            duration=3000
        ).show_toast()

if __name__ == "__main__":
    try:
        app = SecurityMonitorGUI()
        app.run()
    except Exception as e:
        Messagebox.show_error(
            "Erreur Critique",
            f"Une erreur est survenue lors du démarrage:\n{str(e)}"
        )
        sys.exit(1)
