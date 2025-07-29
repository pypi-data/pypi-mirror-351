from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.message import Message
from textual.containers import Grid, Horizontal
from textual.widgets import Label, Button


class AuthScreen(Screen[None]):

    CSS_PATH = "auth.tcss"

    class OpenEditor(Message):
        pass

    def compose(self) -> ComposeResult:
        with Grid():
            yield Label("Клондайк аналитика", id="title")
            yield Label("Интерактивный тренажер Python на вашем компьютере", id="subtitle")

            with Horizontal():
                yield Button("Открыть тренажер",
                             id="open_file_button",
                             variant="success")
                yield Button("Выход",
                             id="exit_button",
                             variant="error")

    @on(Button.Pressed, "#open_file_button")
    def on_login(self) -> None:
        self.app.post_message(AuthScreen.OpenEditor())
        self.app.switch_mode("editor")

    @on(Button.Pressed, "#exit_button")
    def on_exit(self) -> None:
        self.app.exit(0)
