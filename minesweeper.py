#!/bin/env python3

# make a grid
# put mines in it
# calculate mines around square

import sys
from random import randrange

from simple_timer import Timer
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, \
  QGraphicsRectItem, QLCDNumber
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import Qt, QTimer, QObject

from minesweeper_gui import *

isLarge = False
grid_x = 200
grid_y = 200
num_mines = 7500

fail_on_mine = False

if isLarge:
  grid_x *= 100
  grid_y *= 100
  num_mines *= 100

colorMap = {
  1: Qt.blue,
  2: Qt.darkGreen,
  3: Qt.red,
  4: Qt.darkRed,
  5: Qt.magenta,
  6: Qt.cyan,
  7: Qt.green,
  8: Qt.black
}

wid = 30
density = (num_mines / (grid_x * grid_y))
print(density)

grid = []
theTrans = None

# class PaintWidget(QWidget):
#   def paintEvent(self, QPaintEvent):
#     painter = QtGui.QPainter(self)
#     gridWid = 10
#     painter.setPen(Qt.red)
#     # view issue
#     painter.drawRect(10,10,100,100)
#     print("paint")


def main():
  app = QApplication(sys.argv)

  w = QMainWindow()
  w.show()

  ui = Ui_MainWindow()
  ui.setupUi(w)

  setup_stuff(ui)

  app.exec()
  print("done app")


def get_range(mqrect):
  if mqrect.cx > 0:
    x1 = mqrect.cx - 1
  else:
    x1 = mqrect.cx

  if mqrect.cy > 0:
    y1 = mqrect.cy - 1
  else:
    y1 = mqrect.cy

  if mqrect.cx < grid_x - 1:
    x2 = mqrect.cx + 2
  else:
    x2 = mqrect.cx

  if mqrect.cy < grid_y - 1:
    y2 = mqrect.cy + 2
  else:
    y2 = mqrect.cy

  return x1, x2, y1, y2


def get_number(mqrect):
  (x1, x2, y1, y2) = get_range(mqrect)
  num = 0
  for x in range(x1, x2):
    for y in range(y1, y2):
      r = grid[x][y]
      if r.m:
        num += 1
  return num


def do_reveal(mqrect):
  if not mqrect.reveal:
    stack = set()
    stack.add(mqrect)
    while len(stack) > 0:
      # print(len(stack))
      mq = stack.pop()
      mq.reveal = True
      if mq.n is None:
        mq.n = get_number(mq)
      if mq.n == 0:
        # print("zero")
        (x1, x2, y1, y2) = get_range(mq)
        for tx in range(x1, x2):
          for ty in range(y1, y2):
            r = grid[tx][ty]
            if not r.reveal:
              stack.add(r)


class MQRect(QGraphicsRectItem):
  def __init__(self, m, x, y):
    super().__init__()
    self.tWid = 0
    self.font = QFont("monospace", 20, 20, False)
    self.fontMetrics = QFontMetrics(self.font)
    self.n = None
    self.m = m
    self.reveal = False
    self.flagged = False
    self.setFont = False
    self.cx = x
    self.cy = y

  def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
    super().paint(QPainter, QStyleOptionGraphicsItem, QWidget_widget)
    painter = QPainter
    if not self.setFont:
      painter.setFont(self.font)
      # self.setFont = True
    # painter = QtGui.QPainter()
    x = self.rect().x()
    y = self.rect().y()
    rwid = self.rect().width()
    rhgt = self.rect().height()
    if self.reveal:
      if self.m:
        # painter.setPen(Qt.blue)
        dwid = 10
        xd = ((rwid - dwid) / 2)
        yd = ((rhgt - dwid) / 2)
        painter.drawEllipse(xd + x, yd + y, dwid, dwid)
      else:
        # draw the number
        if self.n is None:
          self.n = get_number(self)
        if self.n > 0:
          rect = self.fontMetrics.tightBoundingRect(str(self.n))
          nwid = rect.width()
          nhgt = rect.height()
          xd = ((rwid - nwid) / 2)
          yd = ((rhgt - nhgt) / 2)+nhgt
          painter.setPen(colorMap[self.n])
          painter.drawText(xd + x, yd + y, str(self.n))
    elif self.flagged:
      dwid = 20
      painter.setPen(Qt.blue)
      xd = ((rwid - dwid) / 2)
      yd = ((rhgt - dwid) / 2)
      painter.drawRect(xd + x, yd + y, dwid, dwid)

      painter.setPen(Qt.red)
      rect = self.fontMetrics.tightBoundingRect("!")
      nwid = rect.width()
      nhgt = rect.height()
      xd = ((rwid - nwid) / 2)
      yd = ((rhgt - nhgt) / 2)+nhgt
      painter.drawText(xd + x, yd + y, "!")
    else:
      dwid = 20
      painter.setPen(Qt.blue)
      xd = ((rwid - dwid) / 2)
      yd = ((rhgt - dwid) / 2)
      painter.drawRect(xd + x, yd + y, dwid, dwid)


#
# class MRect(object):
#   def __init__(self, m, rect):
#     self.m = m
#     self.rect = rect


def do_game_over():
  pass


def do_mine_warn():
  pass


def do_clicked_mine():
  if fail_on_mine:
    do_game_over()
  else:
    do_mine_warn()

class MineScene(QGraphicsScene):
  def __init__(self, ui, parent=None):
    """

    :param ui:
    :param parent:
    :return:
    """
    super(MineScene, self).__init__(parent)
    self.minesNotSet = True
    self.ui = ui

  def emitter(self):
    lcd = self.ui.lcdNumber
    # lcd = QLCDNumber()
    lcd.display(self.lcdCnt)
    self.lcdCnt+=1
    print(self.lcdCnt)

  def do_mine_setup(self,r):
    base = set()
    (x1, x2, y1, y2) = get_range(r)
    for tx in range(x1, x2):
      for ty in range(y1, y2):
        base.add(grid[tx][ty])

    num_to_place = num_mines

    while num_to_place > 0:
      x = randrange(0, grid_x)
      y = randrange(0, grid_y)
      mr = grid[x][y]
      if mr.m == 0 and (mr not in base):
        mr.m = 1
        num_to_place -= 1

    self.lcdCnt = 0
    self.timer = QTimer()
    self.timer.setInterval(1000)
    self.timer.setSingleShot(False)
    self.timer.timeout.connect(self.emitter)
    self.timer.start()

    # self.ui

    self.minesNotSet = False

  def mousePressEvent(self, QGraphicsSceneMouseEvent):
    pos = QtCore.QPointF(QGraphicsSceneMouseEvent.scenePos())

    # print(str(pos.x()) + " " + str(pos.y()))
    r = self.itemAt(pos, theTrans)

    mbut = QGraphicsSceneMouseEvent.button()
    if mbut == Qt.LeftButton and not r.flagged:
      if self.minesNotSet:
        self.do_mine_setup(r)
      if r.m:
        do_clicked_mine()
      else:
        do_reveal(r)
    elif mbut == Qt.RightButton:
      r.flagged = not r.flagged
    self.update()


def setup_stuff(ui):
  global theTrans
  # pw = PaintWidget()
  # pw.resize(300,300)
  # pw.show()
  # layout = PyQt5.QtWidgets.QHBoxLayout()
  # layout.addWidget(pw)
  # ui.drawArea.setLayout(layout)

  timer = Timer()

  scene = ui.drawArea.scene()
  theTrans = ui.drawArea.transform()
  if scene is None:
    scene = MineScene(ui)
    # scene = QGraphicsScene()
    ui.drawArea.setScene(scene)

  for x in range(0, grid_x):
    row = []
    xw = x * wid
    for y in range(0, grid_y):
      yw = y * wid
      r = MQRect(0, x, y)
      r.setRect(xw, yw, wid, wid)
      scene.addItem(r)
      row.append(r)
    grid.append(row)

  timer.stop()
  print("done " + str(timer.duration))


if __name__ == '__main__':
  main()
