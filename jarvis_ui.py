import flet as ft
import requests
import pyttsx3
import threading
import re
import speech_recognition as sr

# URL limpia de la API
API_URL = "http://127.0.0.1:8000/api/chat"


def hablar(texto):
    def run_tts():
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        texto_limpio = re.sub(r'[*#_`]', '', texto)
        engine.say(texto_limpio)
        engine.runAndWait()

    hilo_voz = threading.Thread(target=run_tts, daemon=True)
    hilo_voz.start()


def escuchar_microfono(callback_texto):
    def run_stt():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                texto = recognizer.recognize_google(audio, language="es-MX")
                print(f"Transcripción: {texto}")
                callback_texto(texto)
            except sr.WaitTimeoutError:
                print("No se detectó voz.")
            except sr.UnknownValueError:
                print("No se entendió el audio.")
            except Exception as ex:
                print(f"Error en micrófono: {str(ex)}")

    threading.Thread(target=run_stt, daemon=True).start()


def main(page: ft.Page):
    page.title = "JARVIS Interface"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 700
    page.padding = 20

    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )

    def send_message(e):
        user_text = user_input.value
        if not user_text:
            return

        chat_list.controls.append(ft.Text(f"Tú: {user_text}", color=ft.colors.BLUE_200, weight=ft.FontWeight.BOLD))
        user_input.value = ""
        user_input.disabled = True
        page.update()

        try:
            response = requests.post(API_URL, json={"message": user_text})
            if response.status_code == 200:
                jarvis_reply = response.json().get("reply", "Error en la respuesta")
                chat_list.controls.append(ft.Text(f"JARVIS: {jarvis_reply}", color=ft.colors.GREEN_ACCENT_400))
                # Ejecutar la síntesis de voz
                hablar(jarvis_reply)
            else:
                chat_list.controls.append(ft.Text(f"Error de conexión: {response.status_code}", color=ft.colors.RED))
        except Exception as ex:
            chat_list.controls.append(ft.Text(f"Error crítico: {str(ex)}", color=ft.colors.RED))

        user_input.disabled = False
        user_input.focus()
        page.update()

    user_input = ft.TextField(
        hint_text="Escribe tu mensaje...",
        expand=True,
        on_submit=send_message
    )
    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        icon_color=ft.colors.BLUE_200,
        on_click=send_message
    )

    def on_speech_result(texto_transcrito):
        if texto_transcrito:
            user_input.value = texto_transcrito
            page.update()
            send_message(None)

    def start_listening(e):
        mic_button.icon_color = ft.colors.RED_500
        page.update()
        escuchar_microfono(on_speech_result)
        mic_button.icon_color = ft.colors.BLUE_200
        page.update()

    mic_button = ft.IconButton(
        icon=ft.icons.MIC_ROUNDED,
        icon_color=ft.colors.BLUE_200,
        on_click=start_listening
    )

    input_row = ft.Row([user_input, mic_button, send_button])

    page.add(
        ft.Text("SISTEMA CENTRAL JARVIS", size=20, weight=ft.FontWeight.W_900, color=ft.colors.BLUE_500),
        ft.Divider(),
        chat_list,
        input_row
    )

ft.app(target=main)