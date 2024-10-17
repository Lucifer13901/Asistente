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
            print(f"Has dicho: {comando}")
            hablar(f"Has dicho: {comando}")
            return comando.lower().strip()
        except sr.UnknownValueError:
            print("No te he entendido, por favor repite.")
            hablar("No te he entendido, por favor repite.")
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
            model="gpt-3.5-turbo",
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
        tiempo = re.search(r"en (\d+)\s?(minutos|minuto|horas|hora)", comando)
        if tiempo:
            cantidad = int(tiempo.group(1))
            unidad = tiempo.group(2)
            if "hora" in unidad:
                minutos = cantidad * 60
            else:
                minutos = cantidad 

            mensaje = re.sub(r"recordatorio en \d+\s?(minutos|minuto|horas|hora)", "", comando).strip()

            if mensaje:
                hablar(f"Te recordaré: {mensaje} en {cantidad} {unidad}.")
                escribir_en_chat(f"Recordatorio: {mensaje} en {cantidad} {unidad}.")
                time.sleep(minutos * 60)
                hablar(f"Es hora de: {mensaje}")
                escribir_en_chat(f"Es hora de: {mensaje}")
            else:
                hablar("No especificaste un mensaje para el recordatorio.")
                escribir_en_chat("Error: No especificaste un mensaje.")
        else:
            hablar("No pude entender el tiempo del recordatorio. Usa el formato 'recordatorio en X minutos' o 'X horas'.")
            escribir_en_chat("Error: No pude entender el tiempo.")
    except Exception as e:
        print(f"Error al crear el recordatorio: {e}")
        hablar("Hubo un error al crear el recordatorio.")
        escribir_en_chat("Error al crear el recordatorio.")


def abrir_programa(programa):
    try:
        sistema = platform.system().lower()
        
        if sistema == 'windows':
            if 'chrome' in programa.lower():
                os.system("start chrome")
            else:
                os.system(f"start {programa}")
        
        elif sistema == 'linux':
            os.system(f"xdg-open {programa}")
       
        elif sistema == 'darwin':
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
        abrir_programa(comando)
    elif "quién es" in comando or "qué es" in comando:
        buscar_en_wikipedia(comando)
    else:
        preguntar_a_chatgpt(comando)

def escuchar_en_fondo():
    while True:
        comando = escuchar()
        if comando:
            gestionar_tareas(comando)
        time.sleep(1)

def procesar_texto_escrito():
    texto = command_entry.get().lower()
    if texto:
        command_entry.delete(0, tk.END)
        gestionar_tareas(texto)

t = threading.Thread(target=escuchar_en_fondo)
t.daemon = True
t.start()

enviar_button = ttk.Button(root, text="Enviar", command=procesar_texto_escrito)
enviar_button.pack(pady=10)

root.mainloop()
