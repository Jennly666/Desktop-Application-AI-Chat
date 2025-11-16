import flet as ft

class AppStyles:
    PAGE_SETTINGS = {
        "title": "AI Chat",
        "vertical_alignment": ft.MainAxisAlignment.CENTER, 
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
        "padding": 20,
        "bgcolor": ft.Colors.GREY_900,
        "theme_mode": ft.ThemeMode.DARK,
    }

    CHAT_HISTORY = {
        "expand": True,
        "spacing": 10,
        "height": 400,
        "auto_scroll": True,
        "padding": 20,
    }

    MESSAGE_INPUT = {
        "width": 400,
        "height": 50,
        "multiline": False,
        "text_size": 16,
        "color": ft.Colors.WHITE,
        "bgcolor": ft.Colors.GREY_800,
        "border_color": ft.Colors.BLUE_400,
        "cursor_color": ft.Colors.WHITE,
        "content_padding": 10,
        "border_radius": 8,
        "hint_text": "Введите сообщение здесь...",
        "shift_enter": True,
    }

    SEND_BUTTON = {
        "text": "Отправка",
        "icon": ft.icons.SEND,
        "style": ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
        ),
        "tooltip": "Отправить сообщение",
        "height": 40,
        "width": 130,
    }

    SAVE_BUTTON = {
        "text": "Сохранить",
        "icon": ft.icons.SAVE,
        "style": ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_700,
            padding=10,
        ),
        "tooltip": "Сохранить диалог в файл",
        "width": 130,
        "height": 40,
    }

    CLEAR_BUTTON = {
        "text": "Очистить",
        "icon": ft.icons.DELETE,
        "style": ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_700,
            padding=10,
        ),
        "tooltip": "Очистить историю чата",
        "width": 130,
        "height": 40,
    }

    ANALYTICS_BUTTON = {
        "text": "Аналитика",
        "icon": ft.icons.ANALYTICS,
        "style": ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_700,
            padding=10,
        ),
        "tooltip": "Показать аналитику",
        "width": 130,
        "height": 40,
    }

    INPUT_ROW = {
        "spacing": 10,
        "alignment": ft.MainAxisAlignment.SPACE_BETWEEN,
        "width": 920,
    }

    CONTROL_BUTTONS_ROW = {
        "spacing": 20,
        "alignment": ft.MainAxisAlignment.CENTER,
    }

    CONTROLS_COLUMN = {
        "spacing": 20,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
    }

    MAIN_COLUMN = {
        "expand": True,
        "spacing": 20,
        "alignment": ft.MainAxisAlignment.CENTER,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
    }

    MODEL_SEARCH_FIELD = {
        "width": 400,
        "border_radius": 8,
        "bgcolor": ft.Colors.GREY_900,
        "border_color": ft.Colors.GREY_700,
        "color": ft.Colors.WHITE,
        "content_padding": 10,
        "cursor_color": ft.Colors.WHITE,
        "focused_border_color": ft.Colors.BLUE_400,
        "focused_bgcolor": ft.Colors.GREY_800,
        "hint_style": ft.TextStyle(
            color=ft.Colors.GREY_400,
            size=14,
        ),
        "prefix_icon": ft.icons.SEARCH,
        "height": 45,
    }

    MODEL_DROPDOWN = {
        "width": 400,
        "height": 45,
        "border_radius": 8,
        "bgcolor": ft.Colors.GREY_900,
        "border_color": ft.Colors.GREY_700,
        "color": ft.Colors.WHITE,
        "content_padding": 10,
        "focused_border_color": ft.Colors.BLUE_400,
        "focused_bgcolor": ft.Colors.GREY_800,
    }


    MODEL_SELECTION_COLUMN = {
        "spacing": 10,
        "horizontal_alignment": ft.CrossAxisAlignment.CENTER,
        "width": 400,
    }

    BALANCE_TEXT = {
        "size": 16,
        "color": ft.Colors.GREEN_400,
        "weight": ft.FontWeight.BOLD,
    }

    BALANCE_CONTAINER = {
        "padding": 10,
        "bgcolor": ft.Colors.GREY_900,
        "border_radius": 8,
        "border": ft.border.all(1, ft.Colors.GREY_700),
    }

    @staticmethod
    def set_window_size(page: ft.Page):
        page.window.width = 600
        page.window.height = 800
        page.window.resizable = False
