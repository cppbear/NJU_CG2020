#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def bresenham_point(x, y, flag):
    if flag:
        return y, x
    else:
        return x, y


def bspline_mat(u, p_list):
    temp = [-u ** 3 + 3 * u ** 2 - 3 * u + 1, 3 * u ** 3 - 6 * u ** 2 + 4, -3 * u ** 3 + 3 * u ** 2 + 3 * u + 1, u ** 3]
    res = 0.0
    for i in range(4):
        res += temp[i] * p_list[i]
    return res / 6


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                result.append((x0, y))
        else:
            m = (y1 - y0) / (x1 - x0)
            if abs(m) <= 1:
                if x0 > x1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                y = y0
                for x in range(x0, x1 + 1):
                    result.append((x, int(y + 0.5)))
                    y += m
            else:
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                x = x0
                for y in range(y0, y1 + 1):
                    result.append((int(x + 0.5), y))
                    x += 1 / m
    elif algorithm == 'Bresenham':
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                result.append((x0, y))
        elif y0 == y1:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                result.append((x, y0))
        else:
            dx, dy = abs(x1 - x0), abs(y1 - y0)
            flag = False
            if dy > dx:
                flag = True
                dx, dy = dy, dx
                x0, y0, x1, y1 = y0, x0, y1, x1
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            delta = 1
            if y1 - y0 < 0:
                delta = -1
            p = 2 * dy - dx
            y = y0
            result.append(bresenham_point(x0, y0, flag))
            for x in range(x0 + 1, x1 + 1):
                if p < 0:
                    p += 2 * dy
                    result.append(bresenham_point(x, y, flag))
                else:
                    y += delta
                    p += 2 * dy - 2 * dx
                    result.append(bresenham_point(x, y, flag))
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    rx, ry = abs(x1 - x0) // 2, abs(y1 - y0) // 2
    xc, yc = (x0 + x1) // 2, (y0 + y1) // 2
    p = ry ** 2 - rx ** 2 * ry + rx ** 2 / 4
    x, y = 0, ry
    result.extend([(x + xc, y + yc), (x + xc, -y + yc)])
    while ry ** 2 * x < rx ** 2 * y:
        if p < 0:
            result.extend([(x + 1 + xc, y + yc), (-x - 1 + xc, y + yc), (-x - 1 + xc, -y + yc), (x + 1 + xc, -y + yc)])
            p += 2 * ry ** 2 * x + 3 * ry ** 2
        else:
            result.extend([(x + 1 + xc, y - 1 + yc), (-x - 1 + xc, y - 1 + yc), (-x - 1 + xc, -y + 1 + yc),
                           (x + 1 + xc, -y + 1 + yc)])
            p += 2 * ry ** 2 * x - 2 * rx ** 2 * y + 2 * rx ** 2 + 3 * ry ** 2
            y -= 1
        x += 1
    p = ry ** 2 * (x + 1 / 2) ** 2 + rx ** 2 * (y - 1) ** 2 - rx ** 2 * ry ** 2
    while y > 0:
        if p > 0:
            result.extend([(x + xc, y - 1 + yc), (-x + xc, y - 1 + yc), (-x + xc, -y + 1 + yc), (x + xc, -y + 1 + yc)])
            p += -2 * rx ** 2 * y + 3 * rx ** 2
        else:
            result.extend([(x + 1 + xc, y - 1 + yc), (-x - 1 + xc, y - 1 + yc), (-x - 1 + xc, -y + 1 + yc),
                           (x + 1 + xc, -y + 1 + yc)])
            p += 2 * ry ** 2 * x - 2 * rx ** 2 * y + 2 * ry ** 2 + 3 * rx ** 2
            x += 1
        y -= 1
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    du = 0.001
    result = []
    if algorithm == 'Bezier':
        n = len(p_list) - 1
        result.append(p_list[0])
        u = du
        while u < 1:
            res = p_list.copy()
            for i in range(n):
                temp = []
                for j in range(len(res) - 1):
                    x1, y1 = res[j]
                    x2, y2 = res[j + 1]
                    temp.append([(1 - u) * x1 + u * x2, (1 - u) * y1 + u * y2])
                res = temp.copy()
            x, y = int(res[0][0] + 0.5), int(res[0][1] + 0.5)
            result.append([x, y])
            u += du
        result.append(p_list[-1])
    elif algorithm == 'B-spline':
        u = 0
        while u <= 1:
            for i in range(len(p_list) - 3):
                x_list = [point[0] for point in p_list[i:i + 4]]
                y_list = [point[1] for point in p_list[i:i + 4]]
                result.append([int(bspline_mat(u, x_list) + 0.5), int(bspline_mat(u, y_list) + 0.5)])
            u += du
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for p in p_list:
        result.append([p[0] + dx, p[1] + dy])
    return result


def rotate(p_list, x, y, r, unit=True):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :param unit: (bool) 角度单位
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    if unit:
        for p in p_list:
            x1, y1 = p[0] - x, p[1] - y
            # x2 = x1 * math.cos((360 - r) / 180 * math.pi) - y1 * math.sin((360 - r) / 180 * math.pi)
            # y2 = x1 * math.sin((360 - r) / 180 * math.pi) + y1 * math.cos((360 - r) / 180 * math.pi)
            x2 = x1 * math.cos(r / 180 * math.pi) - y1 * math.sin(r / 180 * math.pi)
            y2 = x1 * math.sin(r / 180 * math.pi) + y1 * math.cos(r / 180 * math.pi)
            result.append([int(x2 + 0.5) + x, int(y2 + 0.5) + y])
    else:
        for p in p_list:
            x1, y1 = p[0] - x, p[1] - y
            x2 = x1 * math.cos(r) - y1 * math.sin(r)
            y2 = x1 * math.sin(r) + y1 * math.cos(r)
            result.append([int(x2 + 0.5) + x, int(y2 + 0.5) + y])
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return [[int((res[0] - x) * s + 0.5) + x, int((res[1] - y) * s + 0.5) + y] for res in p_list]


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if algorithm == 'Cohen-Sutherland':
        while True:
            code0_temp = []
            code1_temp = []
            code0_temp.extend([0 if y_max - y0 >= 0 else 1, 0 if y0 - y_min >= 0 else 1, 0 if x_max - x0 >= 0 else 1,
                               0 if x0 - x_min >= 0 else 1])
            code1_temp.extend([0 if y_max - y1 >= 0 else 1, 0 if y1 - y_min >= 0 else 1, 0 if x_max - x1 >= 0 else 1,
                               0 if x1 - x_min >= 0 else 1])
            code0 = code0_temp[0] * 8 + code0_temp[1] * 4 + code0_temp[2] * 2 + code0_temp[3]
            code1 = code1_temp[0] * 8 + code1_temp[1] * 4 + code1_temp[2] * 2 + code1_temp[3]
            if code0 == 0 and code1 == 0:
                return [[int(x0 + 0.5), int(y0 + 0.5)], [int(x1 + 0.5), int(y1 + 0.5)]]
            elif code0 & code1 != 0:
                return []
            else:
                if code0 == 0:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                    code0, code1 = code1, code0
                if code0 & 8 == 8:
                    u = (y_max - y0) / (y1 - y0)
                    x0 += u * (x1 - x0)
                    y0 = y_max
                elif code0 & 4 == 4:
                    u = (y_min - y0) / (y1 - y0)
                    x0 += u * (x1 - x0)
                    y0 = y_min
                elif code0 & 2 == 2:
                    u = (x_max - x0) / (x1 - x0)
                    y0 += u * (y1 - y0)
                    x0 = x_max
                elif code0 & 1 == 1:
                    u = (x_min - x0) / (x1 - x0)
                    y0 += u * (y1 - y0)
                    x0 = x_min
    elif algorithm == 'Liang-Barsky':
        dx, dy = x1 - x0, y1 - y0
        p = [-dx, dx, -dy, dy]
        q = [x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
        u1 = 0
        u2 = 1
        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return []
            elif p[i] < 0:
                u1 = max(u1, q[i] / p[i])
            else:
                u2 = min(u2, q[i] / p[i])
            if u1 > u2:
                return []
        return [[int(x0 + u1 * (x1 - x0) + 0.5), int(y0 + u1 * (y1 - y0) + 0.5)],
                [int(x0 + u2 * (x1 - x0) + 0.5), int(y0 + u2 * (y1 - y0) + 0.5)]]
