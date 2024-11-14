import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import time
from datetime import datetime
import sys
from tkinter import ttk
from urllib.request import urlopen
from PIL import Image, ImageTk
import io

# Initialisation de l'interface principale
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")
root = ctk.CTk()

print("============================================")
print(" ")
print(" ")
print("                 WIM Wizard                  ")
print("                    v1.0                     ")
print("             Powered by Axolotl              ")
print(" ")
print(" ")
print("============================================")

def loading_bar():
    sys.stdout.write("\nLoading: [")
    sys.stdout.flush()
    for i in range(20):
        time.sleep(0.1)
        sys.stdout.write("#")
        sys.stdout.flush()
    sys.stdout.write("] Done!\n")
    sys.stdout.flush()

# Barre de chargement
loading_bar()
print(" ")

# Charger une icône depuis une URL
icon_url = "https://raw.githubusercontent.com/justwinlab/WIM-Wizard/refs/heads/main/icons/icon.png"
try:
    with urlopen(icon_url) as response:
        icon_data = response.read()
        icon_image = Image.open(io.BytesIO(icon_data))
        icon_photo = ImageTk.PhotoImage(icon_image)
        root.iconphoto(False, icon_photo)
except Exception as e:
    print(f"Erreur lors du chargement de l'icône: {e}")

# Création des onglets
tab_view = ctk.CTkTabview(root)
tab_view.pack(fill="both", expand=True)

# Ajout des onglets
tab_view.add("Accueil")
tab_view.add("Mount WIM File")
tab_view.add("Unmount WIM Extracted")
tab_view.add("Build")
root.title("WIM Wizard")
root.geometry("854x480")
root.resizable(False, False)

# Variables globales pour stocker les chemins et log
wim_file_path = ""
mount_dir_path = ""
source_dir_path = ""
unmount_file_path = ""
log_messages = []

# Fonction pour mettre à jour les logs et afficher les messages
def update_log(message):
    log_messages.append(message)
    log_display.configure(state="normal")
    log_display.insert("end", message + "\n")
    log_display.configure(state="disabled")
    log_display.see("end")

# Fonction pour sélectionner un fichier WIM
def select_wim_file():
    global wim_file_path
    wim_file_path = filedialog.askopenfilename(title="Select .wim File", filetypes=[("WIM Files", "*.wim")])
    if wim_file_path:
        wim_file_label.configure(text=f"Selected WIM File: {wim_file_path}")

# Fonction pour sélectionner le dossier de montage
def select_mount_dir():
    global mount_dir_path
    mount_dir_path = filedialog.askdirectory(title="Select Mount Directory")
    if mount_dir_path:
        mount_dir_label.configure(text=f"Mount Directory: {mount_dir_path}")

# Fonction pour sélectionner le dossier ou fichier à démonter
def select_unmount_dir():
    global unmount_file_path
    unmount_file_path = filedialog.askdirectory(title="Select Directory to Unmount")
    if unmount_file_path:
        unmount_dir_label.configure(text=f"Unmount Directory: {unmount_file_path}")

# Fonction pour exécuter une commande avec barre de progression
def execute_command(command, success_message, error_message, buttons_to_disable):
    # Désactiver les boutons avant de commencer
    for button in buttons_to_disable:
        button.configure(state="disabled")

    def redirect_to_accueil():
        tab_view.set("Accueil")
        time.sleep(0.5)

    try:
        update_log(" ")
        update_log("Please wait, operation in progress...")
        redirect_to_accueil()
        root.update()  # Mise à jour de l'interface pour afficher la progression

        # Exécution de la commande
        subprocess.run(command, shell=True, check=True)
        update_log(success_message)

    except subprocess.CalledProcessError:
        update_log(error_message)

    # Réactiver les boutons une fois l'opération terminée
    for button in buttons_to_disable:
        button.configure(state="normal")

# Fonction pour monter un fichier WIM
def mount_wim():
    if wim_file_path and mount_dir_path:
        command = f'dism /mount-wim /wimfile:"{wim_file_path}" /index:1 /mountdir:"{mount_dir_path}"'
        execute_command(command, f"Mounted {wim_file_path} to {mount_dir_path}", "Failed to mount the WIM file.",
                        [mount_button, unmount_apply_button, create_button])

# Fonction pour démonter le WIM avec option de sauvegarde
def unmount_wim_apply():
    save_changes = unmount_option.get() == "Unmount and Save Changes"
    if unmount_file_path:
        command = f'dism /unmount-wim /mountdir:"{unmount_file_path}" {" /commit" if save_changes else " /discard"}'
        execute_command(command,
                        f"Unmounted {'with changes' if save_changes else 'and discarded changes'} from {unmount_file_path}",
                        "Failed to unmount the WIM file.", [mount_button, unmount_apply_button, create_button])

# Fonction pour capturer un dossier en WIM
def create_wim():
    global source_dir_path
    source_dir_path = filedialog.askdirectory(title="Select Source Directory")
    save_path = filedialog.asksaveasfilename(title="Save WIM File As", defaultextension=".wim",
                                             filetypes=[("WIM Files", "*.wim")])
    if source_dir_path and save_path:
        command = f'dism /capture-image /imagefile:"{save_path}" /capturedir:"{source_dir_path}" /name:"Custom_WinPE"'
        execute_command(command, f"Created WIM file at {save_path}", "Failed to create the WIM file.",
                        [mount_button, unmount_apply_button, create_button])

# Fonction pour vérifier le statut du montage
def check_mount_status():
    if mount_dir_path:
        command = f'dism /get-mountedwiminfo'
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            update_log("Mount Status:\n" + result.stdout)
        except subprocess.CalledProcessError:
            update_log("Failed to check mount status.")

# Fonction pour basculer le thème
def switch_theme(theme="System"):
    ctk.set_appearance_mode(theme)
    update_log(f"Switched to {theme} theme")

# Interface avec des options supplémentaires et améliorations
title_label = ctk.CTkLabel(tab_view.tab("Accueil"), text="WIM Wizard", font=("Arial", 20, "bold"))
description_label = ctk.CTkLabel(tab_view.tab("Accueil"),
                                 text="Bienvenue dans WIM Wizard. Le programme de modification de .wim",
                                 font=("Arial", 12))
title_label.pack(pady=10)
description_label.pack(pady=20)

# Section pour les options WIM
wim_frame = ctk.CTkFrame(tab_view.tab("Mount WIM File"))
wim_frame.pack(pady=10, padx=10, fill="x")

wim_section_label = ctk.CTkLabel(wim_frame, text="Mount WIM File", font=("Arial", 20))
wim_section_label.pack(pady=(10, 0))

# Sélection du fichier WIM
wim_file_button = ctk.CTkButton(wim_frame, text="Select WIM File", command=select_wim_file, corner_radius=10, width=150)
wim_file_button.pack(pady=10)
wim_file_label = ctk.CTkLabel(wim_frame, text="Selected WIM File: None")
wim_file_label.pack(pady=5)

# Sélection du répertoire de montage
mount_dir_button = ctk.CTkButton(wim_frame, text="Select Mount Directory", command=select_mount_dir, corner_radius=10,
                                 width=150)
mount_dir_button.pack(pady=10)
mount_dir_label = ctk.CTkLabel(wim_frame, text="Mount Directory: None")
mount_dir_label.pack(pady=5)

# Boutons pour monter, démonter et créer WIM
mount_button = ctk.CTkButton(wim_frame, text="Mount WIM", command=mount_wim, corner_radius=10, width=150)
mount_button.pack(pady=30)

# Section pour démonter WIM
unmount_frame = ctk.CTkFrame(tab_view.tab("Unmount WIM Extracted"))
unmount_frame.pack(pady=10, padx=10, fill="x")

unmount_section_label = ctk.CTkLabel(unmount_frame, text="Unmount WIM Extracted", font=("Arial", 20))
unmount_section_label.pack(pady=(10, 0))

# Sélection du répertoire à démonter
unmount_dir_button = ctk.CTkButton(unmount_frame, text="Select Unmount Directory", command=select_unmount_dir,
                                   corner_radius=10, width=150)
unmount_dir_button.pack(pady=10)
unmount_dir_label = ctk.CTkLabel(unmount_frame, text="Unmount Directory: None")
unmount_dir_label.pack(pady=5)

unmount_option = ctk.CTkOptionMenu(unmount_frame, values=["Unmount and Save Changes", "Unmount and Discard Changes"])
unmount_option.pack(pady=10)

unmount_apply_button = ctk.CTkButton(unmount_frame, text="Unmount", command=unmount_wim_apply, corner_radius=10,
                                     width=150)
unmount_apply_button.pack(pady=30)

# Bouton pour créer WIM
build_frame = ctk.CTkFrame(tab_view.tab("Build"))
build_frame.pack(pady=10, padx=10, fill="x")

label = ctk.CTkLabel(build_frame, text="Build .WIM", font=("Arial", 20))
label.pack(pady=(10, 0))

create_button = ctk.CTkButton(build_frame, text="Create WIM from Folder", command=create_wim, corner_radius=10,
                              width=150)
create_button.pack(pady=10)

# Section pour le statut et log
status_frame = ctk.CTkFrame(tab_view.tab("Accueil"))
status_frame.pack(pady=10, padx=10, fill="x")

status_section_label = ctk.CTkLabel(status_frame, text="Status and Logs", font=("Arial", 16))
status_section_label.pack(pady=(10, 0))

# Zone d'affichage des logs
log_display = ctk.CTkTextbox(status_frame, width=800, height=100, state="disabled")
log_display.pack(pady=10)

# Section pour changer le thème
theme_frame = ctk.CTkFrame(tab_view.tab("Accueil"))
theme_frame.pack(pady=10, padx=10, fill="x")

theme_label = ctk.CTkLabel(theme_frame, text="Switch Theme:", font=("Arial", 12))
theme_label.pack(pady=5)

theme_option = ctk.CTkOptionMenu(theme_frame, values=["System", "Dark", "Light"], command=switch_theme)
theme_option.pack(pady=5)

# Bouton pour quitter l'application
exit_button = ctk.CTkButton(theme_frame, text="Exit", command=root.quit, corner_radius=10, width=100)
exit_button.pack(pady=5)

# Exécute l'interface graphique
root.mainloop()
