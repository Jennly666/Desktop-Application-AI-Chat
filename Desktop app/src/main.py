import flet as ft
from api.openrouter import OpenRouterClient
from ui.styles import AppStyles
from ui.components import MessageBubble, ModelSelector
from utils.cache import ChatCache
from utils.logger import AppLogger
from utils.analytics import Analytics
from utils.monitor import PerformanceMonitor
import asyncio
import time
import json
from datetime import datetime
import os
import random


class ChatApp:
    def __init__(self):
        self.cache = ChatCache()
        self.logger = AppLogger()
        self.analytics = Analytics(self.cache)
        self.monitor = PerformanceMonitor()

        self.api_client: OpenRouterClient | None = None

        self.balance_text = ft.Text(
            "Баланс: н/д",
            **AppStyles.BALANCE_TEXT
        )

        self.exports_dir = "exports"
        os.makedirs(self.exports_dir, exist_ok=True)

        self.model_dropdown = None
        self.message_input = None
        self.chat_history = None
        self.main_column = None

    # ------------------------- АУТЕНТИФИКАЦИЯ -------------------------

    def _generate_pin(self) -> str:
        return f"{random.randint(0, 9999):04d}"

    def _init_api_client(self, api_key: str):
        self.api_client = OpenRouterClient(api_key=api_key)
        self.update_balance()

    def _show_auth_screen_first_time(self, page: ft.Page):
        page.controls.clear()

        api_key_field = ft.TextField(
            label="API ключ OpenRouter",
            hint_text="Введите секретный ключ OpenRouter.ai",
            password=True,
            can_reveal_password=True,
            autofocus=True,
            width=400,
        )
        status_text = ft.Text("", size=14)

        def on_submit_key(e):
            api_key = api_key_field.value.strip()
            if not api_key:
                status_text.value = "Пожалуйста, введите ключ."
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            status_text.value = "Проверяем ключ..."
            status_text.color = ft.Colors.GREY_400
            page.update()

            try:
                temp_client = OpenRouterClient(api_key=api_key)
                balance_str = temp_client.get_balance()

                if balance_str == "Ошибка":
                    raise ValueError(
                        "Не удалось проверить ключ. Убедитесь, что ключ введён правильно."
                    )

                pin = self._generate_pin()
                self.cache.save_auth(api_key=api_key, pin=pin)

                self.api_client = temp_client
                self.update_balance()

                def close_and_open_chat(ev):
                    page.dialog.open = False
                    page.update()
                    self._build_chat_ui(page)

                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("PIN-код создан"),
                    content=ft.Column(
                        [
                            ft.Text(
                                "Ваш 4-значный PIN для входа:",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                pin,
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_400,
                            ),
                            ft.Text(
                                "Обязательно запомните или запишите его.",
                                size=14,
                            ),
                        ],
                        tight=True,
                        spacing=10,
                    ),
                    actions=[ft.TextButton("OK", on_click=close_and_open_chat)],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                page.dialog = dialog
                dialog.open = True
                page.update()

            except Exception as ex:
                self.logger.error(f"Ошибка проверки API ключа: {ex}", exc_info=True)
                status_text.value = f"Ошибка: {ex}"
                status_text.color = ft.Colors.RED_400
                page.update()

        submit_button = ft.ElevatedButton(
            text="Сохранить ключ",
            icon=ft.Icons.KEY,
            on_click=on_submit_key,
        )

        content = ft.Column(
            controls=[
                ft.Text("Первый запуск", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Введите ключ OpenRouter.ai. Мы проверим его валидность, "
                    "сгенерируем 4-значный PIN и откроем приложение.",
                    size=14,
                    color=ft.Colors.GREY_400,
                    width=500,
                    text_align=ft.TextAlign.LEFT,
                ),
                api_key_field,
                submit_button,
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=15,
        )

        page.add(
            ft.Container(
                content=content,
                alignment=ft.alignment.center,
                padding=30,
            )
        )
        page.update()

    def _show_auth_screen_with_pin(self, page: ft.Page, api_key: str, pin: str):
        page.controls.clear()

        pin_field = ft.TextField(
            label="PIN-код",
            hint_text="Введите 4-значный PIN",
            password=True,
            can_reveal_password=True,
            max_length=4,
            width=200,
            autofocus=True,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        status_text = ft.Text("", size=14)

        def on_login(e):
            entered_pin = (pin_field.value or "").strip()
            if len(entered_pin) != 4 or not entered_pin.isdigit():
                status_text.value = "PIN должен содержать 4 цифры."
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            if entered_pin != pin:
                status_text.value = "Неверный PIN."
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            try:
                self._init_api_client(api_key)
            except Exception as ex:
                self.logger.error(f"Ошибка инициализации OpenRouterClient: {ex}", exc_info=True)
                status_text.value = f"Ошибка инициализации клиента: {ex}"
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            self._build_chat_ui(page)

        def on_reset_key(e):
            self.cache.clear_auth()
            self._show_auth_screen_first_time(page)

        login_button = ft.ElevatedButton(
            text="Войти",
            icon=ft.Icons.LOCK_OPEN,
            on_click=on_login,
        )
        reset_button = ft.TextButton(
            text="Сбросить ключ",
            icon=ft.Icons.RESTART_ALT,
            on_click=on_reset_key,
        )

        content = ft.Column(
            controls=[
                ft.Text("Вход", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Введите свой 4-значный PIN. При необходимости вы можете сбросить ключ и настроить всё заново.",
                    size=14,
                    color=ft.Colors.GREY_400,
                    width=500,
                    text_align=ft.TextAlign.LEFT,
                ),
                pin_field,
                ft.Row(
                    controls=[login_button, reset_button],
                    spacing=10,
                ),
                status_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=15,
        )

        page.add(
            ft.Container(
                content=content,
                alignment=ft.alignment.center,
                padding=30,
            )
        )
        page.update()

    # ------------------------- ОСНОВНОЙ UI ЧАТА -------------------------

    def load_chat_history(self):
        try:
            history = self.cache.get_chat_history()
            for msg in reversed(history):
                _, model, user_message, ai_response, timestamp, tokens = msg
                self.chat_history.controls.extend([
                    MessageBubble(message=user_message, is_user=True),
                    MessageBubble(message=ai_response, is_user=False)
                ])
        except Exception as e:
            self.logger.error(f"Ошибка загрузки истории чата: {e}")

    def update_balance(self):
        if not self.api_client:
            self.balance_text.value = "Баланс: н/д"
            self.balance_text.color = ft.Colors.RED_400
            return

        try:
            balance = self.api_client.get_balance()
            self.balance_text.value = f"Баланс: {balance}"
            self.balance_text.color = ft.Colors.GREEN_400
        except Exception as e:
            self.balance_text.value = "Баланс: н/д"
            self.balance_text.color = ft.Colors.RED_400
            self.logger.error(f"Ошибка обновления баланса: {e}")

    def _build_chat_ui(self, page: ft.Page):
        page.controls.clear()

        models = self.api_client.available_models if self.api_client else []
        self.model_dropdown = ModelSelector(models)
        self.model_dropdown.value = models[0]["id"] if models else None

        def show_error_snack(page, message: str):
            snack = ft.SnackBar(
                content=ft.Text(
                    message,
                    color=ft.Colors.RED_500
                ),
                bgcolor=ft.Colors.GREY_900,
                duration=5000,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()

        async def send_message_click(e):
            if not self.message_input.value:
                return

            if not self.api_client:
                show_error_snack(page, "API клиент не инициализирован.")
                return

            try:
                self.message_input.border_color = ft.Colors.BLUE_400
                page.update()

                start_time = time.time()
                user_message = self.message_input.value
                self.message_input.value = ""
                page.update()

                self.chat_history.controls.append(
                    MessageBubble(message=user_message, is_user=True)
                )

                loading = ft.ProgressRing()
                self.chat_history.controls.append(loading)
                page.update()

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.api_client.send_message(
                        user_message,
                        self.model_dropdown.value
                    )
                )

                self.chat_history.controls.remove(loading)

                if "error" in response:
                    response_text = f"Ошибка: {response['error']}"
                    tokens_used = 0
                    self.logger.error(f"Ошибка API: {response['error']}")
                else:
                    response_text = response["choices"][0]["message"]["content"]
                    tokens_used = response.get("usage", {}).get("total_tokens", 0)

                self.cache.save_message(
                    model=self.model_dropdown.value,
                    user_message=user_message,
                    ai_response=response_text,
                    tokens_used=tokens_used
                )

                self.chat_history.controls.append(
                    MessageBubble(message=response_text, is_user=False)
                )

                response_time = time.time() - start_time
                self.analytics.track_message(
                    model=self.model_dropdown.value,
                    message_length=len(user_message),
                    response_time=response_time,
                    tokens_used=tokens_used
                )

                self.monitor.log_metrics(self.logger)
                page.update()

            except Exception as e:
                self.logger.error(f"Ошибка отправки сообщения: {e}")
                self.message_input.border_color = ft.Colors.RED_500

                snack = ft.SnackBar(
                    content=ft.Text(
                        str(e),
                        color=ft.Colors.RED_500,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor=ft.Colors.GREY_900,
                    duration=5000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()

        async def show_analytics(e):
            stats = self.analytics.get_statistics()

            dialog = ft.AlertDialog(
                title=ft.Text("Аналитика"),
                content=ft.Column([
                    ft.Text(f"Всего сообщений: {stats['total_messages']}"),
                    ft.Text(f"Всего токенов: {stats['total_tokens']}"),
                    ft.Text(f"Среднее токенов/сообщение: {stats['tokens_per_message']:.2f}"),
                    ft.Text(f"Сообщений в минуту: {stats['messages_per_minute']:.2f}")
                ]),
                actions=[
                    ft.TextButton("Закрыть", on_click=lambda e: close_dialog(dialog)),
                ],
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        async def clear_history(e):
            try:
                self.cache.clear_history()
                self.analytics.clear_data()
                self.chat_history.controls.clear()
            except Exception as e:
                self.logger.error(f"Ошибка очистки истории: {e}")
                show_error_snack(page, f"Ошибка очистки истории: {str(e)}")

        def close_dialog(dialog):
            dialog.open = False
            page.update()
            if dialog in page.overlay:
                page.overlay.remove(dialog)

        async def confirm_clear_history(e):
            def close_dlg(e):
                close_dialog(dialog)

            async def clear_confirmed(e):
                await clear_history(e)
                close_dialog(dialog)

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Подтверждение удаления"),
                content=ft.Text("Вы уверены? Это действие нельзя отменить!"),
                actions=[
                    ft.TextButton("Отмена", on_click=close_dlg),
                    ft.TextButton("Очистить", on_click=clear_confirmed),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        async def save_dialog(e):
            try:
                history = self.cache.get_chat_history()

                dialog_data = []
                for msg in history:
                    dialog_data.append({
                        "timestamp": msg[4],
                        "model": msg[1],
                        "user_message": msg[2],
                        "ai_response": msg[3],
                        "tokens_used": msg[5]
                    })

                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(self.exports_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(dialog_data, f, ensure_ascii=False, indent=2, default=str)

                dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Диалог сохранен"),
                    content=ft.Column([
                        ft.Text("Путь сохранения:"),
                        ft.Text(filepath, selectable=True, weight=ft.FontWeight.BOLD),
                    ]),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: close_dialog(dialog)),
                        ft.TextButton("Открыть папку",
                            on_click=lambda e: os.startfile(self.exports_dir)
                        ),
                    ],
                )

                page.overlay.append(dialog)
                dialog.open = True
                page.update()

            except Exception as e:
                self.logger.error(f"Ошибка сохранения: {e}")
                show_error_snack(page, f"Ошибка сохранения: {str(e)}")

        # --- построение layout ---

        self.message_input = ft.TextField(**AppStyles.MESSAGE_INPUT)
        self.chat_history = ft.ListView(**AppStyles.CHAT_HISTORY)

        self.load_chat_history()

        save_button = ft.ElevatedButton(
            on_click=save_dialog,
            **AppStyles.SAVE_BUTTON
        )

        clear_button = ft.ElevatedButton(
            on_click=confirm_clear_history,
            **AppStyles.CLEAR_BUTTON
        )

        send_button = ft.ElevatedButton(
            on_click=send_message_click,
            **AppStyles.SEND_BUTTON
        )

        analytics_button = ft.ElevatedButton(
            on_click=show_analytics,
            **AppStyles.ANALYTICS_BUTTON
        )

        control_buttons = ft.Row(
            controls=[
                save_button,
                analytics_button,
                clear_button
            ],
            **AppStyles.CONTROL_BUTTONS_ROW
        )

        input_row = ft.Row(
            controls=[
                self.message_input,
                send_button
            ],
            **AppStyles.INPUT_ROW
        )

        controls_column = ft.Column(
            controls=[
                input_row,
                control_buttons
            ],
            **AppStyles.CONTROLS_COLUMN
        )

        balance_container = ft.Container(
            content=self.balance_text,
            **AppStyles.BALANCE_CONTAINER
        )

        model_selection = ft.Column(
            controls=[
                self.model_dropdown.search_field,
                self.model_dropdown,
                balance_container
            ],
            **AppStyles.MODEL_SELECTION_COLUMN
        )

        self.main_column = ft.Column(
            controls=[
                model_selection,
                self.chat_history,
                controls_column
            ],
            **AppStyles.MAIN_COLUMN
        )

        page.add(self.main_column)
        self.monitor.get_metrics()
        self.logger.info("Приложение запущено")

    # ------------------------- ТОЧКА ВХОДА FLET -------------------------

    def main(self, page: ft.Page):
        for key, value in AppStyles.PAGE_SETTINGS.items():
            setattr(page, key, value)

        AppStyles.set_window_size(page)

        auth_data = self.cache.get_auth()

        if not auth_data:
            self._show_auth_screen_first_time(page)
        else:
            self._show_auth_screen_with_pin(page, api_key=auth_data["api_key"], pin=auth_data["pin"])


def main():
    app = ChatApp()
    ft.app(target=app.main)


if __name__ == "__main__":
    main()
