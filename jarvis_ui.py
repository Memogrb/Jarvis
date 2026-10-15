import flet as ft
import requests
import pyttsx3
import thereading
import re

def hablar(texto):
    def run_tts():
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        texto_limpio = re.sub(r'[*#_`]', '', texto)
        engine.say(texto_limpio)
        engine.runAndWait()

    hilo_voz = thereading.Thread(target=run_tts,deamon=True)
    hilo_voz.start()

API_URL = "[http://127.0.0.1:8000/api/chat](http://127.0.0.1:8000/api/chat)"

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
            else:
                chat_list.controls.append(ft.Text(f"Error de conexión: {response.status_code}", color=ft.colors.RED))
        except Exception as ex:
            chat_list.controls.append(ft.Text(f"Error critico: {str(ex)}", color=ft.colors.RED))

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

    input_row = ft.Row([user_input, send_button])

    page.add(
        ft.Text("SISTEMA CENTRAL JARVIS", size=20, weight=ft.FontWeight.W_900, color=ft.colors.BLUE_500),
        ft.Divider(),
        chat_list,
        input_row
    )

ft.app(target=main)
