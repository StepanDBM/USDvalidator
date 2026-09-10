# extraction/inspection_session.py

from pathlib import Path
from time import perf_counter

from pxr import Usd

from contexts import StageContext

from .stage_health import StageHealthExtractor


class UsdInspectionSession:
    def __init__(self, source_path):
        self.source_path = Path(source_path).expanduser().resolve()
        self.stage = None
        self.health_extractor = StageHealthExtractor()

    def extract(self):
        context = StageContext(
            source_path=str(self.source_path),
            exists=self.source_path.is_file(),
        )

        if not context.exists:
            context.error_message = "The USD file does not exist."
            return [context]

        start_time = perf_counter()

        try:
            self.stage = Usd.Stage.Open(str(self.source_path))
        except Exception as exc:
            context.error_message = str(exc)
            return [context]

        open_duration_seconds = perf_counter() - start_time

        if not self.stage:
            context.error_message = "OpenUSD returned an invalid Stage."
            return [context]

        context.opened = True
        context.root_layer = self.stage.GetRootLayer().identifier

        health_context = self.health_extractor.extract(
            stage=self.stage,
            source_path=self.source_path,
            open_duration_seconds=open_duration_seconds,
        )

        return [
            context,
            health_context,
        ]