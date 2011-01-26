# -*- encoding: utf-8 -*-

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL import GL as gl, GLU as glu

import ui_main


class MainWindow(QtGui.QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.glwidget = GLWidget(self.eval_source, self.verticalLayoutWidget)
        self.glwidget.setObjectName("glwidget")
        self.verticalLayout.addWidget(self.glwidget)
        self.connect(self.runButton, QtCore.SIGNAL('clicked()'), self.update_scene)
        self.textEdit.setPlainText(SAMPLE_SCENE)
        self.scene_source = None
        self.eval_globals = dict(gl.__dict__)
        self.eval_globals.update(glu.__dict__)

    def update_scene(self):
        self.scene_source = unicode(self.textEdit.toPlainText())
        self.glwidget.update()

    def eval_source(self):
        if self.scene_source:
            lines = self.scene_source.split('\n')
            success = True
            for n, line in enumerate(lines):
                if not line: continue
                try:
                    eval(line.strip(';'), self.eval_globals)
                except (NameError, SyntaxError) as e:
                    error = unicode(e).replace('(<string>, line 1)', '')
                    self.statusbar.showMessage(error)
                    lines[n] = u'<font title="%s" color="red">%s</font>' % (error, line)
                    success = False
                    break
            self.textEdit.setHtml('<br/>'.join(lines))
            if success:
                self.statusbar.showMessage('')
    

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, eval_source, parent):
        self.eval_source = eval_source
        super(GLWidget, self).__init__(parent = parent)
    
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
    
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        self.eval_source()


SAMPLE_SCENE = '''glTranslatef(-1.5, 0.0, -6.0)
glBegin(GL_TRIANGLES)
glColor3f(1.0, 0.0, 0.0)
glVertex3f(0.0, 1.0, 0.0)
glColor3f(0.0, 1.0, 0.0)
glVertex3f(-1.0, -1.0, 0.0)
glColor3f(0.0, 0.0, 1.0)
glVertex3f(1.0, -1.0, 0.0)
glEnd()

glLoadIdentity()
glTranslatef(1.5, 0.0, -6.0)
glColor3f(0.5, 0.5, 1.0)
glBegin(GL_QUADS)
glVertex3f(-1.0, 1.0, 0.0)
glVertex3f( 1.0, 1.0, 0.0)
glVertex3f( 1.0,-1.0, 0.0)
glVertex3f(-1.0,-1.0, 0.0)
glEnd()'''


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
