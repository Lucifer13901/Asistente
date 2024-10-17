import tkinter as tk  
from tkinter import ttk
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import openai
import webbrowser
import time
import requests
import re
import threading
import os
import platform

openai.api_key = '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'

engine = pyttsx3.init()

voices = engine.getProperty('voices')
spanish_voices = [voice for voice in voices if 'es' in voice.languages]
if spanish_voices:
    engine.setProperty('voice', spanish_voices[0].id)
else:
    print("No se encontró una voz en español.")
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

root = tk.Tk()
root.title("Asistente Virtual")
root.geometry("500x600")
root.config(bg="#2E3B4E")

background_image = Image.open("fondo.jpg")
background_image = background_image.resize((500, 600), Image.Resampling.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_photo)
background_label.place(relwidth=1, relheight=1)

assistant_image = Image.open("asistente.png")
assistant_image = assistant_image.resize((80, 80), Image.Resampling.LANCZOS)
assistant_photo = ImageTk.PhotoImage(assistant_image)
assistant_label = tk.Label(root, image=assistant_photo, bg="#2E3B4E")
assistant_label.place(x=20, y=20)

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10, relief="flat", background="#4CAF50", foreground="green")
style.configure("TLabel", font=("Helvetica", 12), background="#2E3B4E", foreground="black")
style.configure("TEntry", font=("Helvetica", 12), padding=10)

chat_area = tk.Text(root, width=60, height=20, font=("Helvetica", 12), bg="#F0F0F0", fg="#333333", wrap="word", state=tk.DISABLED)
chat_area.pack(pady=10)

command_entry = ttk.Entry(root, font=("Helvetica", 12), width=30)
command_entry.pack(pady=10)

response_label = ttk.Label(root, text="Comando: Esperando...", font=("Helvetica", 12), background="#2E3B4E", foreground="white")
response_label.pack(pady=5)

def hablar(texto):
    engine.say(texto)
    engine.runAndWait()

def escuchar():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            print("Reconociendo...")
            comando = r.recognize_google(audio, language='es-ES')
            print(f"Marcos has dicho: {comando}")
            hablar(f"Marcos has dicho: {comando}")
            return comando.lower().strip()
        except sr.UnknownValueError:
            print("No te he entendido marcos, por favor repite.")
            hablar("No te he entendido marcos, por favor repite.")
            return ""
        except sr.RequestError:
            print("Error al conectar con el servicio de reconocimiento.")
            hablar("Error al conectar con el servicio de reconocimiento.")
            return ""

def escribir_en_chat(texto):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"Asistente: {texto}\n", "assistant")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)

def preguntar_a_chatgpt(pregunta):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=pregunta,
            max_tokens=150
        )
        respuesta = response.choices[0].text.strip()
        print(f"Respuesta de GPT: {respuesta}")
        hablar(respuesta)
        escribir_en_chat(respuesta)
        response_label.config(text=f"Comando: {pregunta}")
    except Exception as e:
        print(f"Error en la API de GPT: {e}")
        hablar("Hubo un error al consultar la inteligencia artificial.")

def buscar_en_wikipedia(pregunta):
    try:
        query = pregunta.replace("quién es", "").replace("qué es", "").strip()
        url = f"https://es.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exintro&explaintext&titles={query}"
        response = requests.get(url).json()
        page = next(iter(response["query"]["pages"].values()))
        extract = page.get("extract", "No encontré información sobre eso.")
        print(f"Respuesta de Wikipedia: {extract}")
        hablar(extract)
        escribir_en_chat(extract)
        response_label.config(text=f"Comando: {pregunta}")
    except Exception as e:
        print(f"Error al buscar en Wikipedia: {e}")
        hablar("Hubo un error al buscar en Wikipedia.")

def reproducir_musica(comando):
    try:
        song = comando.replace("reproducir música", "").strip()
        if song:
            query = '+'.join(song.split())
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            hablar(f"Reproduciendo música de {song} en YouTube.")
            escribir_en_chat(f"Reproduciendo música de {song}.")
            response_label.config(text=f"Comando: Reproduciendo música de {song}")
        else:
            hablar("No encontré ninguna canción. Intenta de nuevo.")
            escribir_en_chat("No encontré ninguna canción.")
    except Exception as e:
        print(f"Error al reproducir música: {e}")
        hablar("Hubo un error al intentar reproducir música.")

def crear_recordatorio(comando):
    try:
        tiempo = re.search(r"en (\d+) minutos", comando)
        if tiempo:
            minutos = int(tiempo.group(1))
            mensaje = comando.replace(f"en {minutos} minutos", "").strip()
            hablar(f"Te recordaré: {mensaje} en {minutos} minutos.")
            escribir_en_chat(f"Recordatorio: {mensaje} en {minutos} minutos.")
            time.sleep(minutos * 60)
            hablar(f"Es hora de: {mensaje}")
            escribir_en_chat(f"Es hora de: {mensaje}")
        else:
            hablar("No pude entender el recordatorio. Usa el formato 'recordatorio en X minutos'.")
            escribir_en_chat("No pude entender el recordatorio.")
    except Exception as e:
        print(f"Error al crear el recordatorio: {e}")
        hablar("Hubo un error al crear el recordatorio.")

def abrir_programa(programa):
    try:
        # Comprobación multiplataforma
        sistema = platform.system().lower()
        if sistema == 'windows':
            os.system(f"start {programa}")
        elif sistema == 'linux':
            os.system(f"xdg-open {programa}")
        elif sistema == 'darwin':  # macOS
            os.system(f"open {programa}")
        else:
            hablar("No puedo abrir programas en este sistema operativo.")
            escribir_en_chat("No puedo abrir programas en este sistema operativo.")
            return
        hablar(f"Abriendo {programa}.")
        escribir_en_chat(f"Abriendo {programa}.")
        response_label.config(text=f"Comando: Abriendo {programa}")
    except Exception as e:
        print(f"Error al abrir el programa: {e}")
        hablar(f"No pude abrir {programa}.")
        escribir_en_chat(f"No pude abrir {programa}.")
        response_label.config(text=f"Comando: No pude abrir {programa}")

def gestionar_tareas(comando):
    print(f"Comando recibido: {comando}")
    if "reproducir música" in comando:
        reproducir_musica(comando)
    elif "recordatorio" in comando:
        crear_recordatorio(comando)
    elif "abrir" in comando:
        abrir_programa(comando.replace("abrir", "").strip())
    elif "wikipedia" in comando:
        buscar_en_wikipedia(comando)
    else:
        preguntar_a_chatgpt(comando)

def iniciar_comando():
    comando = command_entry.get().strip().lower()
    if comando:
        gestionar_tareas(comando)
    else:
        hablar("No has dado ningún comando. Por favor, intenta de nuevo.")

def escuchar_comando_voz():
    comando = escuchar()
    if comando:
        gestionar_tareas(comando)

boton_escuchar = ttk.Button(root, text="Escuchar", command=lambda: threading.Thread(target=escuchar_comando_voz).start())
boton_escuchar.pack(pady=10)

boton_enviar = ttk.Button(root, text="Enviar", command=iniciar_comando)
boton_enviar.pack(pady=10)

root.mainloop()
