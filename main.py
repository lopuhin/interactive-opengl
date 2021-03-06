# -*- encoding: utf-8 -*-

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL import GL as gl, GLU as glu

import ui_main


class MainWindow(QtGui.QMainWindow, ui_main.Ui_MainWindow):
    hint = 'Press F5 to update scene, use arrows to look around'
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.glwidget = GLWidget(self.eval_source, self.verticalLayoutWidget)
        self.glwidget.setObjectName("glwidget")
        self.verticalLayout.addWidget(self.glwidget)
        self.textEdit.setPlainText(SAMPLE_SCENE)
        self.scene_source = None
        self.eval_globals = dict(gl.__dict__)
        self.eval_globals.update(glu.__dict__)
        self.eval_globals['grid'] = self.glwidget.draw_grid
        del self.eval_globals['glLoadIdentity'] # do not allow
        self.statusbar.showMessage(self.hint)
        self.update_scene()
        self.glwidget.parent().resize(self.size().width() / 2, self.size().height())
        
    def update_scene(self):
        self.scene_source = unicode(self.textEdit.toPlainText())
        self.glwidget.update()

    def eval_source(self):
        if self.scene_source:
            lines = self.scene_source.split('\n')
            success = True
            in_glBegin = False
            for n, line in enumerate(lines):
                if not line: continue
                eval_line = line.strip().strip(';')
                try:
                    eval(eval_line, self.eval_globals)
                except (NameError, SyntaxError) as e:
                    error = unicode(e).replace('(<string>, line 1)', '')
                    self.statusbar.showMessage(error)
                    lines[n] = u'<font title="%s" color="red">%s</font>' % (error, line)
                    if in_glBegin:
                        gl.glEnd()
                        self.glwidget.clear_scene()
                    success = False
                    break
                if eval_line == 'glEnd()':
                    in_glBegin = False
                if eval_line.startswith('glBegin('):
                    in_glBegin = True
            self.textEdit.setHtml('<br/>'.join(lines))
            if success:
                self.statusbar.showMessage(self.hint)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.update_scene()


class GLWidget(QtOpenGL.QGLWidget):
    angle_shift = 0.5
    
    def __init__(self, eval_source, parent):
        self.eval_source = eval_source
        super(GLWidget, self).__init__(parent = parent)
        self.angle_up = 0
        self.angle_right = 0
    
    def initializeGL(self):
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)
    
    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, float(width)/height, 0.1, 100.0)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def mousePressEvent(self, event):
        self.setFocus()

    def keyPressEvent(self, event):
        {QtCore.Qt.Key_Up: self.on_key_up,
         QtCore.Qt.Key_Down: self.on_key_down,
         QtCore.Qt.Key_Left: self.on_key_left,
         QtCore.Qt.Key_Right: self.on_key_right}.get(event.key(), lambda: None)()
        self.update()

    def on_key_up(self):
        self.angle_up += self.angle_shift

    def on_key_down(self):
        self.angle_up -= self.angle_shift

    def on_key_left(self):
        self.angle_right += self.angle_shift

    def on_key_right(self):
        self.angle_right -= self.angle_shift

    def paintGL(self):
        self.clear_scene()
        gl.glRotate(self.angle_up, -1, 0, 0)
        gl.glRotate(self.angle_right, 0, -1, 0)
        self.eval_source()

    def clear_scene(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

    def draw_grid(self):
        ''' Draw coordinate grid in (x, z) plane with y = 0 '''
        grid_size = 10
        grid_coords = range(-grid_size, grid_size + 1)
        gl.glColor3f(0.5, 0.5, 0.5)
        gl.glBegin(gl.GL_LINES)
        for x in grid_coords:
            gl.glVertex3f(x, 0,-grid_size)
            gl.glVertex3f(x, 0, grid_size)
        for z in grid_coords:
            gl.glVertex3f(-grid_size, 0, z)
            gl.glVertex3f( grid_size, 0, z)
        # bright main coordinate lines
        gl.glColor3f(1.0, 1.0, 1.0)
        gl.glVertex3f(-grid_size, 0, 0)
        gl.glVertex3f( grid_size, 0, 0)
        gl.glVertex3f(0, 0,-grid_size)
        gl.glVertex3f(0, 0, grid_size)
        gl.glVertex3f(0,-grid_size, 0)
        gl.glVertex3f(0, grid_size, 0)
        gl.glEnd()
        

SAMPLE_SCENE = '''glTranslatef(-1.5, -1.0, -6.0)
grid()
glBegin(GL_TRIANGLES)
glColor3f(1.0, 0.0, 0.0)
glVertex3f(0.0, 1.0, 0.0)
glColor3f(0.0, 1.0, 0.0)
glVertex3f(-1.0, -1.0, 0.0)
glColor3f(0.0, 0.0, 1.0)
glVertex3f(1.0, -1.0, 0.0)
glEnd()

glTranslatef(3.5, 0.0, 0.0)
grid()
glColor3f(0.5, 0.5, 1.0)
glBegin(GL_QUADS)
glVertex3f(-1.0, 1.0, 0.0)
glVertex3f( 1.0, 1.0, 0.0)
glVertex3f( 1.0,-1.0, 0.0)
glVertex3f(-1.0,-1.0, 0.0)
glEnd()
'''


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
