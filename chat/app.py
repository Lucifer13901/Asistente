import re  
import os  
import time  
import threading  
import platform  
import webbrowser  
import tkinter as tk  
from tkinter import ttk
import google.generativeai as gai

# Función para hablar (Simulando la función de texto a voz)  
def hablar(texto):  
    os.system(f'say "{texto}"')  # Cambia esto según tu sistema operativo  

# Función para escribir en el chat (Simulando la escritura en un chat)  
def escribir_en_chat(mensaje):  
    pass  # Implementa aquí según tu interfaz de usuario  

# Función para preguntar a Gemini  
def preguntar_a_gemini(pregunta):  
    try:  
        response = gemini_api.ask(pregunta)  # Aquí debe ir tu llamada real a la API de Gemini  
        respuesta = response.get("respuesta", "No se obtuvo respuesta.")  
        
        print(f"Respuesta de Gemini: {respuesta}")  
        hablar(respuesta)  
        escribir_en_chat(respuesta)  
        response_label.config(text=f"Comando: {pregunta}")  
    except Exception as e:  
        print(f"Error en la API de Gemini: {e}")  
        hablar("Hubo un error al consultar la inteligencia artificial.")  

# Funciones de gestión de tareas  
def gestionar_tareas(comando):  
    print(f"Comando recibido: {comando}")  
    if "reproducir música" in comando:  
        reproducir_musica(comando)  
    elif "recordatorio" in comando:  
        crear_recordatorio(comando)  
    elif "abrir" in comando:  
        abrir_programa(comando)  
    elif "quién es" in comando or "qué es" in comando:  
        buscar_en_wikipedia(comando)  
    else:  
        preguntar_a_gemini(comando)  # Llamar a la función de Gemini  

# Función para reproducir música  
def reproducir_musica(song):  
    print(f"Reproduciendo música: {song}")  
    # Implementa la funcionalidad real para reproducir música aquí  

# Función para crear un recordatorio  
def crear_recordatorio(comando):  
    print(f"Creando recordatorio: {comando}")  
    # Implementa la funcionalidad real para crear recordatorios aquí  

# Función para abrir un programa  
def abrir_programa(programa):  
    print(f"Abrir programa: {programa}")  
    # Implementa la funcionalidad real para abrir programas aquí  

# Función para buscar en Wikipedia  
def buscar_en_wikipedia(query):  
    print(f"Buscando en Wikipedia: {query}")  
    webbrowser.open(f"https://es.wikipedia.org/wiki/{re.sub(' ', '_', query)}")  

# Función para escuchar comandos (simulando reconocimiento de voz)  
def escuchar():  
    # Simula el reconocimiento de voz o simplemente captura texto de entrada  
    return command_entry.get()  # Obtener texto del campo de entrada  

# Hilo para escuchar en segundo plano  
def escuchar_en_fondo():  
    while True:  
        comando = escuchar()  
        if comando:  
            gestionar_tareas(comando)  
        time.sleep(1)  

# Configuración de la interfaz de usuario  
root = tk.Tk()  
root.title("Asistente Virtual")  

command_entry = ttk.Entry(root)  
command_entry.pack(pady=10)  

send_button = ttk.Button(root, text="Enviar", command=lambda: gestionar_tareas(command_entry.get()))  
send_button.pack(pady=10)  

response_label = ttk.Label(root, text="")  
response_label.pack(pady=10)  

# Iniciar hilo de escucha  
t = threading.Thread(target=escuchar_en_fondo)  
t.daemon = True  
t.start()  

root.mainloop()