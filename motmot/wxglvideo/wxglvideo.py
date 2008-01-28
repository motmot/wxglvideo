# $Id: $
import wx
import wx.glcanvas
import pyglet.gl as gl
import pyglet.gl

# XXX TODO:
#  check off-by-one error in width/coordinate settings (e.g. glOrtho call)
#  allow sharing of OpenGL context between instances

class PygWxContext:
    _gl_begin = False
    _workaround_unpack_row_length = False
    def __init__(self, glcanvas ):
        # glcanvas is instance of wx.glcanvas.GLCanvas
        self.glcanvas = glcanvas
        pyglet.gl._contexts.append( self )

    def SetCurrent(self):
        pyglet.gl._current_context = self
        self.glcanvas.SetCurrent()

class DynamicImageCanvas(wx.glcanvas.GLCanvas):
    def _setcurrent(self,hack_ok=True):
        self.wxcontext.SetCurrent()

    def __init__(self, *args, **kw):
        super(DynamicImageCanvas, self).__init__(*args,**kw)
        self.init = False

        self.flip_lr = False
        self.fullcanvas = False
        self.rotate_180 = False

        wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_PAINT(self, self.OnPaint)
        self._pygimage = None

        self.wxcontext = PygWxContext( self )
        self.wxcontext.SetCurrent()

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW. (inhereted from wxDemo)

    def set_flip_lr(self,value):
        self.flip_lr = value
        self._reset_projection()
    def set_fullcanvas(self,value):
        self.fullcanvas = value
        self._reset_projection()
    def set_rotate_180(self,value):
        self.rotate_180 = value
        self._reset_projection()

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.GetContext():
            self.wxcontext.SetCurrent()
            gl.glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.wxcontext.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def InitGL(self):
        self.wxcontext.SetCurrent()
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        self._reset_projection()
        self.extra_initgl()

    def extra_initgl(self):
        pass

    def _reset_projection(self):
        if self.fullcanvas:
            if self._pygimage is None:
                return
            width, height = self._pygimage.width, self._pygimage.height
        else:
            size = self.GetClientSize()
            width, height = size.width, size.height

        b = 0
        t = height

        if self.flip_lr:
            l = width
            r = 0
        else:
            l = 0
            r = width

        if self.rotate_180:
            l,r=r,l
            b,t=t,b

        if width==0 or height==0:
            # prevent OpenGL error
            return

        self.wxcontext.SetCurrent()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(l,r,b,t, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def new_image(self, image):
        self._pygimage = image
        self._reset_projection() # always trigger re-calculation of projection - necessary if self.fullcanvas

    def update_image(self, image):
        self.wxcontext.SetCurrent()
        self._pygimage.view_new_array( image )

    def core_draw(self):
        if self._pygimage is not None:
            self._pygimage.blit(0, 0, 0)

    def OnDraw(self):
        self.wxcontext.SetCurrent()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.core_draw()
        self.SwapBuffers()
