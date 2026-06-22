# -----------------------------------------------------------
# AUTHOR --------> Francisco Jose Contreras Cuevas
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel)

from .player_panel import player
from .stocks_panel import stocks

from ..nuke_util.panels import panel_widget
from .stocks import load_data


class status_bar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(layout)

        self.total_label = QLabel()
        self.indexing_stock = QLabel()
        self.current_stock = QLabel()
        self.visibles_label = QLabel()

        layout.addWidget(self.current_stock)
        layout.addStretch()
        layout.addWidget(self.total_label)
        layout.addWidget(self.indexing_stock)
        layout.addStretch()
        layout.addWidget(self.visibles_label)

    def set_current_stock(self, stock):
        width, height = stock['resolution']

        data_text = '<font color="#64C8FA"><i>{}x{}</i></font>'.format(
            width, height)

        left_text = '{} - {}'.format(stock['name'], data_text)
        right_text = '<font color="#ffbb00"><b>{}</b></font> frames'.format( stock['frames'])

        if stock['frames'] == 1:
            right_text = 'Texture'

        text = '{} - {}'.format(left_text, right_text)

        self.current_stock.setText(text)

    def set_visibles_label(self, visibles, total):

        visibles_text = '<font color="{}">{} / </font>'.format(
            '#00ff40' if visibles == total else '#c4c4c4', visibles)

        total_text = '<font color="{}">{}</font>'.format(
            '#00ff40' if visibles == total else '#ffbb00', total)

        text = '{} {}'.format(visibles_text, total_text)
        self.visibles_label.setText(text)


class stock_manager_widget(panel_widget):
    def __init__(self, parent=None):
        panel_widget.__init__(self, parent)
        self.mounted = False

    def setup(self):
        self.mounted = True

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        viewer_layout = QVBoxLayout()
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer = QWidget()
        viewer.setLayout(viewer_layout)

        _status_bar = status_bar()
        _player = player()
        _stocks = stocks(_player, _status_bar)

        viewer_layout.addWidget(_player)
        viewer_layout.addWidget(_stocks)

        layout.addWidget(viewer)
        layout.addWidget(_status_bar)

        self.setLayout(layout)
        load_data()
        _stocks.refresh_stocks()

    def showEvent(self, event):
        super(stock_manager_widget, self).showEvent(event)

        if not self.mounted:
            self.setup()
