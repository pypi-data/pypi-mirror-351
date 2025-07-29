from __future__ import annotations
from typing import Any
from textual import on
from textual.message import Message
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Vertical
from textual.reactive import var
from textual.widgets import (
    Header,
    Footer
)


from python_coach.datacontext.dc import DataContext
from python_coach.ui.editor_screen.actions.init_action import InitAction
from python_coach.ui.editor_screen.components.code_editor import CodeEditor
from python_coach.ui.editor_screen.components.current_task import CurrentTaskInfo
from python_coach.ui.editor_screen.components.explorer import Explorer
from python_coach.ui.editor_screen.components.quiz_description import QuizDescription
from python_coach.ui.editor_screen.components.test_results import TestResults

from python_coach.ui.file_screen.open_file_screen import OpenFileScreen
from python_coach.ui.state.app_state import (
    INITIAL_STATE,
    AppState)

from python_coach.ui.editor_screen.actions.editor_actions import (
    BaseAction,
    MakeQuizCurrentAction,
    MakeTaskCurrentAction,
    QuizNodeCollapseAction,
    QuizNodeExpandAction,
    RunCodeAndSetResultsAction,
    UpdateCodeAction)
from python_coach.ui.state.app_reducer import app_dispatch


class EditorScreen(Screen[Any]):
    CSS_PATH = "editor.tcss"

    state = var(INITIAL_STATE, init=False)

    BINDINGS = [
        ('ctrl+r', 'run_btn_click', 'Запустить код'),
        ('ctrl+o', 'open_quiz_file', 'Открыть тест')
    ]

    class UpdateAppTitleMessage(Message):
        def __init__(self, title: str, subtitle: str) -> None:
            super().__init__()
            self.title = title
            self.subtitle = subtitle

    class RequestOpenFileScreen(Message):
        pass

    def watch_state(self, new_state: AppState):
        explorer = self.query_one("Explorer", Explorer)
        code_editor = self.query_one("CodeEditor", CodeEditor)
        task_info = self.query_one("CurrentTaskInfo", CurrentTaskInfo)
        test_results = self.query_one("TestResults", TestResults)
        quiz_description = self.query_one("QuizDescription", QuizDescription)

        explorer.state = new_state
        code_editor.state = new_state
        task_info.state = new_state
        test_results.state = new_state
        quiz_description.state = new_state

        # send message to update title and subtitle
        self.post_message(EditorScreen.UpdateAppTitleMessage(
            new_state.current.app_title,
            new_state.current.app_subtitle
        ))
        # update component visibility
        if new_state.current.object_name == "task":
            code_editor.remove_class("component-hidden")
            quiz_description.add_class("component-hidden")
        elif new_state.current.object_name == "quiz":
            code_editor.add_class("component-hidden")
            quiz_description.remove_class("component-hidden")
        elif new_state.current.object_name == "account":
            pass

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Vertical(id="left_panel"):
            yield Explorer()
            yield CurrentTaskInfo()
        with Vertical(id="right_panel"):
            yield CodeEditor()
            yield QuizDescription(classes="component-hidden")
            yield TestResults()

    @on(Explorer.TaskSelected)
    def on_python_task_selected(self, ev: Explorer.TaskSelected) -> None:
        if isinstance(ev.task_id, int):
            self.dispatch(MakeTaskCurrentAction(ev.task_id))

    @on(Explorer.QuizSelected)
    def on_quiz_selected(self, ev: Explorer.QuizSelected) -> None:
        self.dispatch(MakeQuizCurrentAction(quiz_id=ev.quiz_id))

    @on(Explorer.QuizNodeExpandedOrCollapsed)
    def on_quiz_node_expanded_collapsed(self, ev: Explorer.QuizNodeExpandedOrCollapsed) -> None:
        if ev.action_type == "expanded":
            self.dispatch(QuizNodeExpandAction(quiz_id=ev.quiz_id))
        elif ev.action_type == "collapsed":
            self.dispatch(QuizNodeCollapseAction(quiz_id=ev.quiz_id))

    @on(CodeEditor.CodeUpdated)
    def on_editor_code_updated(self, ev: CodeEditor.CodeUpdated) -> None:
        self.dispatch(UpdateCodeAction(ev.code))

    def action_run_btn_click(self) -> None:
        self.dispatch(RunCodeAndSetResultsAction())

    def action_open_quiz_file(self) -> None:
        def _on_file_selected(file_path: str | None) -> None:
            if not isinstance(self.app.screen, EditorScreen):
                return
            if file_path is None:
                return
            context = DataContext()
            load_result = context.get_quiz_json(file_path)

            editor_screen: EditorScreen = self.app.screen
            editor_screen.state = app_dispatch(
                editor_screen.state,
                InitAction(data=load_result)
            )

        self.app.push_screen(OpenFileScreen(), _on_file_selected)

    def dispatch(self, action: BaseAction) -> None:
        self.state = app_dispatch(self.state, action)
