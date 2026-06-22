# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
import os

from PySide2.QtCore import (Qt, QTimeLine)
from PySide2.QtGui import (QPixmap, QIcon)
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider)

from ..nuke_util.nuke_util import get_nuke_path
from ..env import INDEXED_DIR


class slider(QSlider):
    def __init__(self):
        QSlider.__init__(self)

        self.setOrientation(Qt.Horizontal)

    def mouseMoveEvent(self, event):
        percent = event.x() * 100 / self.width()
        self.set_value(percent)

    def mousePressEvent(self, event):
        percent = event.x() * 100 / self.width()
        self.set_value(percent)
        super(slider, self).mousePressEvent(event)

    def set_value(self, value):
        self.setValue(value)

class player(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.timeline = QTimeLine()
        self.timeline.setUpdateInterval(1)
        self.timeline.setCurveShape(QTimeLine.LinearCurve)
        self.timeline.frameChanged.connect(self.set_frame)
        self.timeline.finished.connect(self.stop)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_widget = QWidget()
        control_widget.setLayout(control_layout)

        self.time_slider = slider()
        self.time_slider.valueChanged.connect(self.set_frame_by_percent)
        self.time_slider.sliderPressed.connect(
            lambda: (self.stop(), self.set_frame_by_percent(self.time_slider.value())))
        self.frame_counter = QLabel('0')
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(
            QIcon('{0}/stock_manager/icons/pause.png'.format(get_nuke_path())))
        self.play_pause_btn.clicked.connect(self.play_pause_toggle)

        control_layout.addWidget(self.frame_counter)
        control_layout.addWidget(self.time_slider)
        control_layout.addWidget(self.play_pause_btn)

        self.label_view = QLabel()
        self.label_view.setFixedHeight(400)
        self.label_view.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label_view.setStyleSheet("QLabel {background-color: black}")

        layout.addWidget(self.label_view)
        layout.addWidget(control_widget)

        self.playing = False
        self.image_path = ''
        self.frames = 300
        self.frame = 0

        self.time_slider.setEnabled(False)
        self.play_pause_btn.setEnabled(False)

    def set_path(self, name, relative_path, src_frames, resolution):
        path = os.path.join(INDEXED_DIR, relative_path)
        self.image_path = path
        self.name = name
        self.resolution = resolution

        w, h = self.resolution
        if not w or not h:
            return

        is_texture = src_frames == 1

        self.time_slider.setEnabled(not is_texture)
        self.play_pause_btn.setEnabled(not is_texture)

        if is_texture:
            self.stop()
            self.time_slider.set_value(0)
            self.set_pixmap('{}/{}.jpg'.format(path, name))
            self.frame_counter.setText('')
            return

        max_frames = 300
        self.frames = max_frames if max_frames < src_frames else src_frames

        self.stop()
        self.frame = 1
        self.play()

    def set_frame_by_percent(self, percent):
        if self.playing:
            return

        percent += 1
        frame = int(percent * self.frames / 100)
        self.set_frame(frame, False)

    def set_frame(self, frame, set_in_slider=True):
        image_path = '{}/{}_{}.jpg'.format(self.image_path, self.name, frame)
        self.set_pixmap(image_path)

        self.frame_counter.setText(str(frame))

        if set_in_slider:
            value = (frame * 100) / self.frames
            self.time_slider.set_value(value)

        self.frame = frame

    def set_pixmap(self, image_path):

        image = QPixmap(image_path)

        w, h = self.resolution
        width = self.label_view.width()
        height = self.label_view.height()

        if w > h and width / height < w / h:
            image = image.scaledToWidth(width, Qt.SmoothTransformation)
        elif width / height < w / h:
            image = image.scaledToWidth(width, Qt.SmoothTransformation)
        else:
            image = image.scaledToHeight(height, Qt.SmoothTransformation)

        self.label_view.setPixmap(image)

    def play_pause_toggle(self):
        self.playing = not self.playing

        if self.playing:
            self.play()
        else:
            self.stop()

    def play(self):
        self.playing = True

        if self.frame >= self.frames:
            self.frame = 1

        frame_length = (float(self.frames - self.frame) / 30) * 1000
        self.timeline.setDuration(int(frame_length))
        self.timeline.setFrameRange(self.frame, self.frames)

        self.timeline.start()

        self.play_pause_btn.setIcon(
            QIcon('{0}/stock_manager/icons/pause.png'.format(get_nuke_path())))

    def stop(self):
        self.playing = False
        self.timeline.stop()

        self.play_pause_btn.setIcon(
            QIcon('{0}/stock_manager/icons/play.png'.format(get_nuke_path())))
