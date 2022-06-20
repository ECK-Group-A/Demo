from rich.panel import Panel

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget

class Hover(Widget):

    # def __init__(self):
    #     super().__init__()
    #     self.contents = "LOL"

    def on_mount(self):
        self.set_interval(0.1, self.refresh)

    def render(self) -> Panel:
        self.console.print("TEST")
        return Panel("TEST")

class SimpleApp(App):

    async def on_mount(self) -> None:
        await self.view.dock(Hover(), edge="left", size=40)
        await self.view.dock(Hover(), Hover(), edge="top")


SimpleApp.run(log="textual.log")

from rich.panel import Panel

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget