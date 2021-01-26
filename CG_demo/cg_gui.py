#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
import pickle
import numpy as np
from PIL import Image
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QColorDialog,
    QGraphicsRectItem,
    QInputDialog,
    QFileDialog,
    QMessageBox)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import *


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.temp_color = QColor(0, 0, 0)
        self.origin_pos = None
        self.trans_center = None
        self.origin_p_list = None
        self.border = None

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_ellipse(self, algorithm, item_id):
        self.status = 'ellipse'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
        self.temp_item = None

    def start_translate(self):
        self.status = 'translate'
        self.temp_item = None

    def start_rotate(self):
        self.status = 'rotate'
        self.temp_item = None
        self.trans_center = None
        self.origin_p_list = None

    def start_scale(self):
        self.status = 'scale'
        self.temp_item = None
        self.trans_center = None
        self.origin_p_list = None

    def start_clip(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm
        self.temp_item = None
        self.origin_pos = None
        self.origin_p_list = None

    def start_delete(self):
        if self.selected_id != '':
            self.main_window.is_modified = True
            self.temp_item = self.item_dict[self.selected_id]
            number = self.list_widget.findItems(self.selected_id, Qt.MatchContains)
            row = self.list_widget.row(number[0])
            # self.list_widget.removeItemWidget(self.number[0])
            temp_id = self.selected_id
            self.clear_selection()
            self.list_widget.clearSelection()
            self.scene().removeItem(self.temp_item)
            self.temp_item = None
            del self.item_dict[temp_id]
            self.list_widget.takeItem(row)
            self.updateScene([self.sceneRect()])

    def start_freedom(self, item_id):
        self.status = 'freedom'
        self.temp_id = item_id
        self.temp_item = None

    def finish_draw(self):
        self.temp_id = self.main_window.get_id(True)

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if self.status == 'polygon' or self.status == 'curve':
            self.finish_draw()
        self.trans_center = None
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        if selected != '':
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.status = ''
            self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # print('press')
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.temp_color)
            self.scene().addItem(self.temp_item)
            self.main_window.is_modified = True
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.temp_color)
            self.scene().addItem(self.temp_item)
            self.main_window.is_modified = True
        elif self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list.append([x, y])
            self.main_window.is_modified = True
        elif self.status == 'translate':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_pos = pos
                self.origin_p_list = self.temp_item.p_list
        elif self.status == 'rotate':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
                if self.trans_center is None:
                    self.trans_center = pos
                else:
                    self.origin_pos = pos
        elif self.status == 'scale':
            if self.selected_id != '':
                self.main_window.is_modified = True
                self.temp_item = self.item_dict[self.selected_id]
                self.origin_p_list = self.temp_item.p_list
                if self.trans_center is None:
                    self.trans_center = pos
                else:
                    self.origin_pos = pos
        elif self.status == 'clip':
            if self.selected_id != '':
                self.temp_item = self.item_dict[self.selected_id]
                if self.temp_item.item_type == 'line':
                    self.main_window.is_modified = True
                    self.origin_pos = pos
                    self.origin_p_list = self.temp_item.p_list
        elif self.status == 'freedom':
            self.main_window.is_modified = True
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], '', self.temp_color)
            self.scene().addItem(self.temp_item)
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'curve':
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            if self.selected_id != '':
                dx = x - int(self.origin_pos.x())
                dy = y - int(self.origin_pos.y())
                self.temp_item.p_list = alg.translate(self.origin_p_list, dx, dy)
        elif self.status == 'rotate':
            if self.selected_id != '' and self.trans_center is not None and self.origin_pos is not None:
                x_origin, y_origin = int(self.origin_pos.x() - self.trans_center.x()), int(
                    self.origin_pos.y() - self.trans_center.y())
                len_origin = math.sqrt(x_origin ** 2 + y_origin ** 2)
                x_now, y_now = x - int(self.trans_center.x()), y - int(self.trans_center.y())
                len_now = math.sqrt(x_now ** 2 + y_now ** 2)
                if len_origin != 0 and len_now != 0:
                    sin_origin = y_origin / len_origin
                    cos_origin = x_origin / len_origin
                    sin_now = y_now / len_now
                    cos_now = x_now / len_now
                    delta_sin = sin_now * cos_origin - cos_now * sin_origin
                    delta_cos = cos_now * cos_origin + sin_now * sin_origin
                    if delta_cos >= 0:
                        r = math.asin(delta_sin)
                    else:
                        r = math.pi - math.asin(delta_sin)
                    self.temp_item.p_list = alg.rotate(self.origin_p_list, int(self.trans_center.x()),
                                                       int(self.trans_center.y()), r, False)
        elif self.status == 'scale':
            if self.selected_id != '' and self.trans_center is not None and self.origin_pos is not None:
                x_last, y_last = int(self.origin_pos.x() - self.trans_center.x()), int(
                    self.origin_pos.y() - self.trans_center.y())
                len_last = math.sqrt(x_last ** 2 + y_last ** 2)
                if len_last != 0:
                    x_now, y_now = x - int(self.trans_center.x()), y - int(self.trans_center.y())
                    len_now = math.sqrt(x_now ** 2 + y_now ** 2)
                    self.temp_item.p_list = alg.scale(self.origin_p_list, int(self.trans_center.x()),
                                                      int(self.trans_center.y()), len_now / len_last)
        elif self.status == 'clip':
            if self.selected_id != '' and self.origin_pos is not None and self.temp_item.item_type == 'line':
                x_min = min(int(self.origin_pos.x()), x)
                x_max = max(int(self.origin_pos.x()), x)
                y_min = min(int(self.origin_pos.y()), y)
                y_max = max(int(self.origin_pos.y()), y)
                '''
                self.temp_item.p_list = alg.clip(self.origin_p_list, x_min, y_min, x_max, y_max, self.temp_algorithm)
                print(self.temp_item.p_list)
                '''
                if self.border is None:
                    self.border = QGraphicsRectItem(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
                    self.scene().addItem(self.border)
                    self.border.setPen(QColor(0, 255, 255))
                else:
                    self.border.setRect(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
        elif self.status == 'freedom':
            self.temp_item.p_list.append([x, y])
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon':
            self.item_dict[self.temp_id] = self.temp_item
            if not self.list_widget.findItems(self.temp_id, Qt.MatchContains):
                self.list_widget.addItem(self.temp_id)
        elif self.status == 'curve':
            self.item_dict[self.temp_id] = self.temp_item
            if not self.list_widget.findItems(self.temp_id, Qt.MatchContains):
                self.list_widget.addItem(self.temp_id)
        elif self.status == 'clip':
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = int(pos.y())
            if self.selected_id != '' and self.origin_pos is not None and self.temp_item.item_type == 'line':
                x_min = min(int(self.origin_pos.x()), x)
                x_max = max(int(self.origin_pos.x()), x)
                y_min = min(int(self.origin_pos.y()), y)
                y_max = max(int(self.origin_pos.y()), y)
                temp_p_list = alg.clip(self.origin_p_list, x_min, y_min, x_max, y_max, self.temp_algorithm)
                if len(temp_p_list) == 0:
                    # self.selected_id = ''
                    # print(self.number)
                    number = self.list_widget.findItems(self.selected_id, Qt.MatchContains)
                    row = self.list_widget.row(number[0])
                    # self.list_widget.removeItemWidget(self.number[0])
                    temp_id = self.selected_id
                    self.clear_selection()
                    self.list_widget.clearSelection()
                    self.scene().removeItem(self.temp_item)
                    self.temp_item = None
                    del self.item_dict[temp_id]
                    self.list_widget.takeItem(row)
                else:
                    self.temp_item.p_list = temp_p_list
            if self.border is not None:
                self.scene().removeItem(self.border)
                self.border = None
            self.updateScene([self.sceneRect()])
        elif self.status == 'freedom':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color=QColor(0, 0, 0),
                 parent: QGraphicsItem = None):
        """
        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            cont_pixels = alg.draw_polygon(self.p_list, 'Bresenham')
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            painter.setPen(QColor(0, 0, 255))
            for p in cont_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'freedom':
            item_pixels = []
            for i in range(len(self.p_list) - 1):
                item_pixels.extend(alg.draw_line([self.p_list[i], self.p_list[i + 1]], 'Bresenham'))
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve' or self.item_type == 'freedom':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for point in self.p_list:
                if point[0] < x_min:
                    x_min = point[0]
                if point[1] < y_min:
                    y_min = point[1]
                if point[0] > x_max:
                    x_max = point[0]
                if point[1] > y_max:
                    y_max = point[1]
            w = x_max - x_min
            h = y_max - y_min
            return QRectF(x_min - 1, y_min - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        # TODO: 区分长宽
        # self.size = 900
        self.length = 800
        self.width = 800
        self.is_modified = False
        self.opened_filename = ''

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(150)
        # self.list_widget.setMaximumWidth(150)
        # self.list_widget.setFixedWidth(150)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.length, self.width)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.length, self.width)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        open_canvas_act = file_menu.addAction('打开画布')
        open_canvas_act.setShortcut('Ctrl+O')
        reset_canvas_act = file_menu.addAction('重置画布')
        reset_canvas_act.setShortcut('Ctrl+R')
        save_canvas_act = file_menu.addAction('保存画布')
        save_canvas_act.setShortcut('Ctrl+S')
        export_canvas_act = file_menu.addAction('导出画布')
        export_canvas_act.setShortcut('Ctrl+E')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        freedom_act = draw_menu.addAction('自由绘图')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        delete_act = edit_menu.addAction('删除')
        delete_act.setShortcut('Delete')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        exit_act.triggered.connect(self.my_quit)
        # exit_act.triggered.connect(self.close)
        set_pen_act.triggered.connect(self.set_pen_action)
        open_canvas_act.triggered.connect(self.open_canvas_action)
        reset_canvas_act.triggered.connect(lambda: self.reset_canvas_action())
        save_canvas_act.triggered.connect(self.save_canvas_action)
        export_canvas_act.triggered.connect(self.export_canvas_action)
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        delete_act.triggered.connect(self.delete_action)
        freedom_act.triggered.connect(self.freedom_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        # self.resize(self.size, self.size)
        self.resize(self.length, self.width)
        self.setWindowTitle('CG Demo')

    def get_id(self, add):
        # _id = str(self.item_cnt)
        if add:
            self.item_cnt += 1
        _id = str(self.item_cnt)
        return _id

    def set_pen_action(self):
        temp_color = QColorDialog.getColor()
        if temp_color.isValid():
            self.canvas_widget.temp_color = temp_color

    def open_canvas_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.statusBar().showMessage('打开画布')
        if len(self.canvas_widget.item_dict) > 0 or self.is_modified:
            reply = QMessageBox.question(self, '是否保存', '是否保存当前草稿？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            # print(reply)
            if reply == QMessageBox.Yes:
                self.save_canvas_action()
            elif reply == QMessageBox.Cancel:
                return
        self.reset_canvas_action(False)
        self.statusBar().showMessage('打开画布')
        path = QFileDialog.getOpenFileName(caption='打开画布', filter='画布文件 (*.canvas)')
        # print(path[0])
        self.opened_filename = path[0]
        if path[0] != '':
            fr = open(path[0], 'rb')
            open_list = pickle.load(fr)
            for item in open_list:
                color = QColor(item[4][0], item[4][1], item[4][2])
                temp_item = MyItem(item[0], item[1], item[2], item[3], color)
                self.canvas_widget.scene().addItem(temp_item)
                self.list_widget.addItem(item[0])
                self.canvas_widget.item_dict[item[0]] = temp_item
            fr.close()
            self.item_cnt = len(open_list)
            name = self.opened_filename.split('/')[-1].split('.')[0]
            self.setWindowTitle('CG Demo - ' + name)

    def reset_canvas_action(self, resize=True):
        # print(resize)
        if resize:
            self.length = QInputDialog.getInt(self, '请输入', '长度', 800, 200, 1500)[0]
            self.width = QInputDialog.getInt(self, '请输入', '宽度', 800, 200, 900)[0]
        self.list_widget.clearSelection()
        self.list_widget.clear()
        self.canvas_widget.clear_selection()
        self.canvas_widget.item_dict.clear()
        self.canvas_widget.scene().clear()
        self.item_cnt = 0
        self.canvas_widget.status = ''
        self.opened_filename = ''
        self.is_modified = False
        # TODO: 设置长宽
        self.scene.setSceneRect(0, 0, self.length, self.width)
        self.canvas_widget.setFixedSize(self.length, self.width)
        self.setWindowTitle('CG Demo')
        # self.resize(self.length, self.width)
        # self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])

    def save_canvas_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.statusBar().showMessage('保存画布')
        save_list = []
        if self.opened_filename == '':
            path = QFileDialog.getSaveFileName(caption='保存画布', filter='画布文件 (*.canvas)')
            # print(path[0])
            if path[0] != '':
                for item in self.canvas_widget.item_dict.values():
                    save_list.append([item.id, item.item_type, item.p_list, item.algorithm, item.color.getRgb()])
                fw = open(path[0], 'wb')
                pickle.dump(save_list, fw)
                fw.close()
                self.opened_filename = path[0]
                self.is_modified = False
                name = self.opened_filename.split('/')[-1].split('.')[0]
                self.setWindowTitle('CG Demo - ' + name)
        else:
            for item in self.canvas_widget.item_dict.values():
                save_list.append([item.id, item.item_type, item.p_list, item.algorithm, item.color.getRgb()])
            fw = open(self.opened_filename, 'wb')
            pickle.dump(save_list, fw)
            fw.close()
            self.is_modified = False

    def export_canvas_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.statusBar().showMessage('导出画布')
        # TODO: 区分长宽
        self.start_export(self.length, self.width)

    def my_quit(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        if self.is_modified:
            reply = QMessageBox.question(self, '退出 - 是否保存', '是否保存当前草稿？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_canvas_action()
                qApp.quit()
            elif reply == QMessageBox.No:
                qApp.quit()
        else:
            qApp.quit()

    def line_naive_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_line('Naive', self.get_id(False))
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_line('DDA', self.get_id(False))
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_line('Bresenham', self.get_id(False))
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_polygon('DDA', self.get_id(False))
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id(False))
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_ellipse('Midpoint-circle', self.get_id(False))
        self.statusBar().showMessage('中点生成算法绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_curve('Bezier', self.get_id(False))
        self.statusBar().showMessage('Bezier曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_draw_curve('B-spline', self.get_id(False))
        self.statusBar().showMessage('B-spline曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def translate_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移')

    def rotate_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转')

    def scale_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放')

    def clip_cohen_sutherland_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland裁剪')

    def clip_liang_barsky_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky裁剪')

    def delete_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_delete()
        self.statusBar().showMessage('删除')

    def freedom_action(self):
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        self.canvas_widget.start_freedom(self.get_id(False))
        self.statusBar().showMessage('自由绘图')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def start_export(self, length, width):
        # TODO: 区分长宽
        path = QFileDialog.getSaveFileName(caption='导出画布', filter='BMP图像 (*.bmp);;PNG图像 (*.png);;JPEG图像 (*.jpg)')
        # print(path)
        if path[0] != '':
            canvas = np.zeros([width, length, 3], np.uint8)
            canvas.fill(255)
            for item in self.canvas_widget.item_dict.values():
                if item.item_type == 'line':
                    pixels = alg.draw_line(item.p_list, item.algorithm)
                    temp_color = item.color.getRgb()
                    pen_color = np.zeros(3, np.uint8)
                    pen_color[0], pen_color[1], pen_color[2] = temp_color[0], temp_color[1], temp_color[2]
                    for x, y in pixels:
                        if 0 <= x < length and 0 <= y < width:
                            canvas[y, x] = np.array(pen_color)
                elif item.item_type == 'polygon':
                    pixels = alg.draw_polygon(item.p_list, item.algorithm)
                    temp_color = item.color.getRgb()
                    pen_color = np.zeros(3, np.uint8)
                    pen_color[0], pen_color[1], pen_color[2] = temp_color[0], temp_color[1], temp_color[2]
                    for x, y in pixels:
                        if 0 <= x < length and 0 <= y < width:
                            canvas[y, x] = np.array(pen_color)
                elif item.item_type == 'ellipse':
                    pixels = alg.draw_ellipse(item.p_list)
                    temp_color = item.color.getRgb()
                    pen_color = np.zeros(3, np.uint8)
                    pen_color[0], pen_color[1], pen_color[2] = temp_color[0], temp_color[1], temp_color[2]
                    for x, y in pixels:
                        if 0 <= x < length and 0 <= y < width:
                            canvas[y, x] = np.array(pen_color)
                elif item.item_type == 'curve':
                    pixels = alg.draw_curve(item.p_list, item.algorithm)
                    temp_color = item.color.getRgb()
                    pen_color = np.zeros(3, np.uint8)
                    pen_color[0], pen_color[1], pen_color[2] = temp_color[0], temp_color[1], temp_color[2]
                    for x, y in pixels:
                        if 0 <= x < length and 0 <= y < width:
                            canvas[y, x] = np.array(pen_color)
                elif item.item_type == 'freedom':
                    pixels = []
                    for i in range(len(item.p_list) - 1):
                        pixels.extend(alg.draw_line([item.p_list[i], item.p_list[i + 1]], 'Bresenham'))
                    temp_color = item.color.getRgb()
                    pen_color = np.zeros(3, np.uint8)
                    pen_color[0], pen_color[1], pen_color[2] = temp_color[0], temp_color[1], temp_color[2]
                    for x, y in pixels:
                        if 0 <= x < length and 0 <= y < width:
                            canvas[y, x] = np.array(pen_color)
                if path[1] == 'BMP图像 (*.bmp)':
                    Image.fromarray(canvas).save(path[0], 'bmp')
                elif path[1] == 'PNG图像 (*.png)':
                    Image.fromarray(canvas).save(path[0], 'png')
                else:
                    Image.fromarray(canvas).save(path[0], 'jpeg', quality=95)

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.canvas_widget.status == 'polygon' or self.canvas_widget.status == 'curve':
            self.canvas_widget.finish_draw()
        if self.is_modified:
            reply = QMessageBox.question(self, '退出 - 是否保存', '是否保存当前草稿？', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self.save_canvas_action()
                a0.accept()
            elif reply == QMessageBox.Cancel:
                a0.ignore()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
