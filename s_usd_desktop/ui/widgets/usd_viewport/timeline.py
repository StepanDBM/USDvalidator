from __future__ import annotations

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QPushButton, QSlider, QWidget


from s_usd_desktop.ui.tooltips import TooltipText


class TimelineWidget(QWidget):
    time_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stage_minimum = 0.0
        self.stage_maximum = 0.0
        self.playback_start = 0.0
        self.playback_end = 0.0
        self.frames_per_second = 24.0
        self.current_time = 0.0
        self._playing = False
        self._updating = False
        self._sample_provider = lambda: ()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)
        self._build_ui()
        self.setEnabled(False)

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        self.to_start = QPushButton("|<")
        self.previous_sample = QPushButton("<|")
        self.previous_frame = QPushButton("<")
        self.play = QPushButton("Play")
        self.next_frame = QPushButton(">")
        self.next_sample = QPushButton("|>")
        self.to_end = QPushButton(">|")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 10000)

        self.start_box = self._time_box()
        self.time_box = self._time_box()
        self.end_box = self._time_box()
        self.range_label = QLabel("Stage 0 - 0 @ 24 fps")
        self.to_start.setToolTip(TooltipText.VIEWPORT_FIRST_FRAME)
        self.previous_sample.setToolTip(
            "Jump to the previous authored time sample within the playback range."
        )
        self.previous_frame.setToolTip(TooltipText.VIEWPORT_STEP_PREVIOUS)
        self.play.setToolTip(TooltipText.VIEWPORT_PLAY)
        self.next_frame.setToolTip(TooltipText.VIEWPORT_STEP_NEXT)
        self.next_sample.setToolTip(
            "Jump to the next authored time sample within the playback range."
        )
        self.to_end.setToolTip(TooltipText.VIEWPORT_LAST_FRAME)
        self.slider.setToolTip(TooltipText.VIEWPORT_TIMELINE)
        self.start_box.setToolTip(
            "Playback start time. Playback loops from the Out value back to this In value."
        )
        self.time_box.setToolTip(TooltipText.VIEWPORT_TIMELINE)
        self.end_box.setToolTip(
            "Playback end time. Values outside the authored stage range may show held or default values."
        )
        self.range_label.setToolTip(TooltipText.VIEWPORT_TIMELINE)

        for widget in (
            self.to_start, self.previous_sample, self.previous_frame,
            self.play, self.next_frame, self.next_sample, self.to_end,
            QLabel("In"), self.start_box, self.slider, self.time_box,
            QLabel("Out"), self.end_box, self.range_label,
        ):
            layout.addWidget(widget)
        layout.setStretchFactor(self.slider, 1)

        self.to_start.clicked.connect(lambda: self.set_time(self.playback_start, emit=True))
        self.to_end.clicked.connect(lambda: self.set_time(self.playback_end, emit=True))
        self.previous_frame.clicked.connect(lambda: self.step(-1.0))
        self.next_frame.clicked.connect(lambda: self.step(1.0))
        self.previous_sample.clicked.connect(lambda: self._step_sample(-1))
        self.next_sample.clicked.connect(lambda: self._step_sample(1))
        self.play.clicked.connect(self.toggle_playback)
        self.slider.valueChanged.connect(self._slider_changed)
        self.time_box.valueChanged.connect(self._time_changed)
        self.start_box.valueChanged.connect(self._playback_start_changed)
        self.end_box.valueChanged.connect(self._playback_end_changed)

    @staticmethod
    def _time_box():
        box = QDoubleSpinBox()
        box.setDecimals(3)
        box.setKeyboardTracking(False)
        return box

    def set_stage(self, stage):
        self.stop()
        if not stage:
            self.setEnabled(False)
            return

        authored_start, authored_end = authored_time_range(stage)
        stage_end = max(0.0, float(stage.GetEndTimeCode()), authored_end or 0.0)
        stage_start = max(0.0, float(stage.GetStartTimeCode()))
        self.stage_minimum = 0.0
        self.stage_maximum = stage_end
        self.frames_per_second = max(1.0, float(stage.GetFramesPerSecond() or 24.0))

        automatic_start = authored_start if authored_start is not None else stage_start
        automatic_end = authored_end if authored_end is not None else stage_end
        automatic_start = max(self.stage_minimum, min(automatic_start, self.stage_maximum))
        automatic_end = max(automatic_start, min(automatic_end, self.stage_maximum))

        self._updating = True
        for box in (self.start_box, self.time_box, self.end_box):
            box.setRange(self.stage_minimum, self.stage_maximum)
        self.playback_start = automatic_start
        self.playback_end = automatic_end
        self.start_box.setValue(automatic_start)
        self.end_box.setValue(automatic_end)
        self.start_box.setMaximum(automatic_end)
        self.end_box.setMinimum(automatic_start)
        self.range_label.setText(
            f"Stage {self.stage_minimum:g} - {self.stage_maximum:g} @ {self.frames_per_second:g} fps"
        )
        self._updating = False
        self.setEnabled(True)
        self.set_time(automatic_start, emit=True)

    def set_sample_provider(self, provider):
        self._sample_provider = provider

    def set_time(self, value, emit=False):
        value = min(self.playback_end, max(self.playback_start, float(value)))
        self.current_time = value
        self._updating = True
        span = self.playback_end - self.playback_start
        slider_value = round((value - self.playback_start) * 10000 / span) if span else 0
        self.slider.setValue(slider_value)
        self.time_box.setValue(value)
        self._updating = False
        if emit:
            self.time_changed.emit(value)

    def step(self, amount):
        self.set_time(self.current_time + amount, emit=True)

    def toggle_playback(self):
        if self._playing:
            self.stop()
            return
        self._playing = True
        self.play.setText("Stop")
        self.timer.start(max(1, round(1000 / self.frames_per_second)))

    def stop(self):
        self._playing = False
        self.timer.stop()
        if hasattr(self, "play"):
            self.play.setText("Play")

    def _playback_start_changed(self, value):
        if self._updating:
            return
        self.playback_start = min(float(value), self.playback_end)
        self.end_box.setMinimum(self.playback_start)
        if self.current_time < self.playback_start:
            self.set_time(self.playback_start, emit=True)
        else:
            self.set_time(self.current_time)

    def _playback_end_changed(self, value):
        if self._updating:
            return
        self.playback_end = max(float(value), self.playback_start)
        self.start_box.setMaximum(self.playback_end)
        if self.current_time > self.playback_end:
            self.set_time(self.playback_end, emit=True)
        else:
            self.set_time(self.current_time)

    def _advance(self):
        value = self.current_time + 1.0
        if value > self.playback_end:
            value = self.playback_start
        self.set_time(value, emit=True)

    def _step_sample(self, direction):
        samples = sorted({
            float(value) for value in self._sample_provider()
            if self.playback_start <= float(value) <= self.playback_end
        })
        candidates = [value for value in samples if value > self.current_time] if direction > 0 else [value for value in samples if value < self.current_time]
        if candidates:
            self.set_time(candidates[0] if direction > 0 else candidates[-1], emit=True)

    def _slider_changed(self, value):
        if self._updating:
            return
        span = self.playback_end - self.playback_start
        self.set_time(self.playback_start + span * value / 10000, emit=True)

    def _time_changed(self, value):
        if not self._updating:
            self.set_time(value, emit=True)


def authored_time_range(stage):
    minimum = None
    maximum = None
    for prim in stage.TraverseAll():
        for attribute in prim.GetAttributes():
            samples = attribute.GetTimeSamples()
            if not samples:
                continue
            first = float(samples[0])
            last = float(samples[-1])
            minimum = first if minimum is None else min(minimum, first)
            maximum = last if maximum is None else max(maximum, last)
    return minimum, maximum
