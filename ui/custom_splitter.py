"""
custom_splitter.py

CustomSplitter and CustomSplitterHandle: QSplitter subclass that prevents full collapse and shows a label for collapsed regions.

Features:
- If a region is collapsed, the handle displays a label (rotated for horizontal splitters).
- Always leaves a visible handle for restoration.
- Theme-aware and supports transparent backgrounds.
- Pane labels can be set via addWidget for user-friendly UI.
"""
from PyQt5.QtWidgets import QSplitter, QSplitterHandle
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QPainter, QFont, QPen


class CustomSplitterHandle(QSplitterHandle):
    def __init__(self, orientation, parent, label="Collapsed"):
        """
        Custom splitter handle that can display a label when a pane is collapsed.
        The handle is theme-aware and supports transparent backgrounds.
        """
        super().__init__(orientation, parent)
        self._label = label
        self._collapsed = False
        self._handle_margin = 8

    def set_collapsed(self, collapsed):
        """
        Set the collapsed state of the handle. Adjusts width for horizontal splitters.
        """
        self._collapsed = collapsed
        if self.orientation() == Qt.Vertical:
            pass
        else:
            if self._collapsed:
                self.setMinimumWidth(40)
                self.setMaximumWidth(40)
            else:
                self.setMinimumWidth(16)
                self.setMaximumWidth(40)
        self.update()

    def set_label(self, label):
        """
        Set the label to display when the handle is collapsed.
        """
        self._label = label
        self.update()

    def paintEvent(self, event):
        """
        Paint the splitter handle, showing a label if collapsed. Uses theme colors and transparency.
        """
        painter = QPainter(self)
        rect = self.rect()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBackgroundMode(Qt.TransparentMode)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        palette = self.palette()
        bg_color = palette.window().color()
        border_color = palette.mid().color()
        text_color = palette.text().color()
        margin = self._handle_margin
        inner_rect = rect.adjusted(margin, margin, -margin, -margin)
        painter.fillRect(inner_rect, bg_color)
        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(inner_rect)
        if self._collapsed and self._label:
            painter.setPen(text_color)
            font = QFont()
            font.setBold(True)
            font.setPointSize(8)
            painter.setFont(font)
            label_rect = inner_rect.adjusted(6, 0, -6, 0)
            if self.orientation() == Qt.Horizontal:
                painter.save()
                painter.translate(rect.center())
                painter.rotate(-90)
                text_rect = QRect(-rect.height()//2 + 6, -rect.width()//2, rect.height() - 12, rect.width())
                painter.drawText(text_rect, Qt.AlignCenter, self._label)
                painter.restore()
            else:
                painter.drawText(label_rect, Qt.AlignCenter, self._label)


class CustomSplitter(QSplitter):
    def __init__(self, orientation, parent=None, collapsed_label="Collapsed"):
        """
        Custom splitter that prevents full collapse and shows a label for collapsed regions.
        Use addWidget(widget, label) to set pane labels.
        """
        super().__init__(orientation, parent)
        self._collapsed_label = collapsed_label
        self._widget_labels = {}
        if orientation == Qt.Vertical:
            self.setHandleWidth(16)
        else:
            self.setHandleWidth(16)
        self.splitterMoved.connect(self._update_all_handles)

    def addWidget(self, widget, label=None):
        """
        Add a widget to the splitter, optionally with a label for collapsed state.
        :param widget: QWidget to add
        :param label: Optional label for the pane (shown when collapsed)
        """
        super().addWidget(widget)
        self._widget_labels[widget] = label if label is not None else "..."
        return widget

    def _update_all_handles(self, pos=None, index=None):
        """
        Update all handles to reflect the current collapsed/expanded state and labels.
        """
        sizes = self.sizes()
        for i, size in enumerate(sizes):
            collapsed = size <= 1
            label = getattr(self, '_collapsed_label', None)
            if not label:
                label = "Metadata" if self.orientation() == Qt.Vertical else "Content"
            self.set_collapsed(i, collapsed, label=label)

    def createHandle(self):
        """
        Create a custom splitter handle.
        """
        return CustomSplitterHandle(self.orientation(), self, self._collapsed_label)

    def set_collapsed(self, index, collapsed=True, label=None):
        """
        Update handle and widget state for collapsed/expanded panes.
        """
        for i in range(1, self.count()):
            left_widget = self.widget(i - 1)
            right_widget = self.widget(i)
            left_collapsed = left_widget.width() <= 1 or left_widget.height() <= 1
            right_collapsed = right_widget.width() <= 1 or right_widget.height() <= 1
            handle = self.handle(i)

            def get_label_for_widget(w):
                if w in self._widget_labels:
                    return self._widget_labels[w]
                if hasattr(w, 'windowTitle') and w.windowTitle():
                    return w.windowTitle()
                elif w.objectName():
                    return w.objectName()
                elif hasattr(w, '__class__'):
                    name = w.__class__.__name__
                    if 'metadata' in name.lower():
                        return 'Metadata'
                    if 'content' in name.lower():
                        return 'Content'
                    return name
                return "Panel"

            if isinstance(handle, CustomSplitterHandle):
                if left_collapsed:
                    dynamic_label = get_label_for_widget(left_widget)
                    handle.set_collapsed(True)
                    handle.set_label(dynamic_label)
                    self.setHandleWidth(40)
                elif right_collapsed:
                    dynamic_label = get_label_for_widget(right_widget)
                    handle.set_collapsed(True)
                    handle.set_label(dynamic_label)
                    self.setHandleWidth(40)
                else:
                    handle.set_collapsed(False)
                    handle.set_label("")
                    self.setHandleWidth(16)
                handle.update()
        widget = self.widget(index)
        if widget:
            if not hasattr(widget, '_original_min_size'):
                widget._original_min_size = widget.minimumSize()
            if collapsed:
                if self.orientation() == Qt.Horizontal:
                    widget.setMinimumWidth(0)
                else:
                    widget.setMinimumHeight(0)
                widget.resize(0, 0)
            else:
                orig = getattr(widget, '_original_min_size', QSize(80, 80))
                widget.setMinimumSize(orig)
                widget.resize(max(orig.width(), 80), max(orig.height(), 80))
                widget.setVisible(True)

    # Optionally, override moveSplitter to prevent full collapse
    def moveSplitter(self, pos, index):
        """
        Prevent full collapse by enforcing a minimum size for each pane.
        """
        min_size = 24
        max_pos = self.size().width() if self.orientation() == Qt.Horizontal else self.size().height()
        if pos < min_size:
            pos = min_size
        elif pos > max_pos - min_size:
            pos = max_pos - min_size
        super().moveSplitter(pos, index)
        sizes = self.sizes()
        for i, size in enumerate(sizes):
            collapsed = size <= 1
            label = getattr(self, '_collapsed_label', None)
            if not label:
                label = "Metadata" if self.orientation() == Qt.Vertical else "Content"
            self.set_collapsed(i, collapsed, label=label)
