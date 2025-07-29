from typing import Any
from textual import on
from textual.app import App

from python_coach.ui.auth_screen.auth import AuthScreen
from python_coach.ui.editor_screen.editor import EditorScreen


class RunnerApp(App[Any]):
    COMMAND_PALETTE_BINDING = "ctrl+backslash"

    MODES = {  # type: ignore
        "editor": EditorScreen,
        "auth": AuthScreen
    }

    def on_mount(self) -> None:
        self.switch_mode("auth")
        self.theme = "gruvbox"
        self.title = "Клондайк аналитика"
        self.sub_title = "Интерактивный тренажер Python на вашем компьютере"

    @on(AuthScreen.OpenEditor)
    def on_auth_success(self) -> None:
        self.switch_mode("editor")

    @on(EditorScreen.UpdateAppTitleMessage)
    def on_title_subtitle_changed(self, event: EditorScreen.UpdateAppTitleMessage) -> None:
        self.title = event.title
        self.sub_title = event.subtitle
