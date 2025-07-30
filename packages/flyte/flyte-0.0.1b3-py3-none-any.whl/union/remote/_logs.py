import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, AsyncIterator

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from union._api_commons import syncer
from union._initialize import get_client, requires_client
from union._protos.logs.dataplane import payload_pb2
from union._protos.workflow import run_definition_pb2, run_logs_service_pb2


class AsyncLogViewer:
    def __init__(self, log_source: AsyncIterator, max_lines: int = 30):
        self.console = Console()
        self.log_source = log_source
        self.max_lines = max_lines
        self.lines = []

    def _format_line(self, logline: payload_pb2.LogLine) -> Text:
        style_map = {
            payload_pb2.LogLineOriginator.SYSTEM: "dim",
            payload_pb2.LogLineOriginator.USER: "cyan",
            payload_pb2.LogLineOriginator.UNKNOWN: "light red",
        }
        style = style_map.get(logline.originator, "")
        return Text(
            f"[{logline.originator}] [{logline.timestamp.ToDatetime().isoformat()}]{logline.message}", style=style
        )

    def _render(self):
        log_text = Text()
        for line in self.lines[-self.max_lines :]:
            log_text.append(line + "\n")
        return Panel(log_text, title="Async Log Viewer", border_style="cyan")

    async def run(self):
        with Live(self._render(), refresh_per_second=10, console=self.console) as live:
            try:
                async for logline in self.log_source:
                    formatted = self._format_line(logline)
                    self.lines.append(formatted)
                    live.update(self._render())
            except asyncio.CancelledError:
                pass


@dataclass
class Logs:
    @classmethod
    @requires_client
    @syncer.wrap
    async def tail(cls, action_id: run_definition_pb2.ActionIdentifier, attempt: int = 1) -> AsyncGenerator[str, None]:
        """
        Tail the logs for a given action ID and attempt.
        :param action_id: The action ID to tail logs for.
        :param attempt: The attempt number (default is 0).
        """
        resp = get_client().logs_service.TailLogs(
            run_logs_service_pb2.TailLogsRequest(action_id=action_id, attempt=attempt)
        )
        async for log_set in resp:
            if log_set.logs:
                for log in log_set.logs:
                    for line in log.lines:
                        yield line

    @classmethod
    async def create_viewer(cls, action_id: run_definition_pb2.ActionIdentifier, attempt: int = 1, max_lines: int = 30):
        viewer = AsyncLogViewer(log_source=cls.tail.aio(cls, action_id=action_id, attempt=attempt), max_lines=max_lines)
        await viewer.run()
