import wx
import wx.xrc as xrc
import pkg_resources
import numpy

from pygarrayimage.arrayimage import ArrayInterfaceImage

import motmot.wxglvideo.wxglvideo as vid

RESFILE = pkg_resources.resource_filename(__name__,"demo.xrc") # trigger extraction

RES = xrc.EmptyXmlResource()
RES.LoadFromString(open(RESFILE).read())

SIZE = 32,32,3

class DemoApp(wx.App):

    def OnInit(self,*args,**kw):
        wx.InitAllImageHandlers()

        self.frame = RES.LoadFrame(None,"DEMO_FRAME") # make frame main panel
        self.frame.Show()

        self.target_panel = xrc.XRCCTRL(self.frame,"TARGET_PANEL")
        self.target_box = wx.BoxSizer(wx.HORIZONTAL)
        self.target_panel.SetSizer(self.target_box)

        ctrl = xrc.XRCCTRL(self.frame,"ADD_DISPLAY")
        wx.EVT_BUTTON(ctrl, ctrl.GetId(), self.OnAddDisplay)

        wx.EVT_CLOSE(self.frame, self.OnWindowClose)

        self.gl_canvases = []
        ID_Timer = wx.NewId()
        self.timer = wx.Timer(self, ID_Timer)
        wx.EVT_TIMER(self, ID_Timer, self.OnTimer)
        self.update_interval=5 # msec
        self.timer.Start(self.update_interval)

        self.widgets2canv = {}

        return True

    def OnWindowClose(self,event):
        self.timer.Stop()
        event.Skip()

    def OnAddDisplay(self,event):
        new_panel = RES.LoadPanel(self.target_panel,"DEMO_PANEL")

        self.target_box.Add( new_panel, 1, wx.EXPAND )

        main_display_panel = xrc.XRCCTRL(new_panel, "MAIN_DISPLAY_PANEL")
        box = wx.BoxSizer(wx.VERTICAL)
        main_display_panel.SetSizer(box)

        # The Hide()/Show() pair prevent a gtk_widget_set_colormap()
        # GTK_WIDGET_REALIZED warning.

        main_display_panel.Hide()
        try:
            gl_canvas = vid.DynamicImageCanvas(main_display_panel,-1)
        finally:
            main_display_panel.Show()

        box.Add(gl_canvas,1,wx.EXPAND)

        self.target_panel.Layout()

        ctrl = xrc.XRCCTRL(new_panel,"FLIPLR")
        self.widgets2canv[ctrl]=gl_canvas
        wx.EVT_CHECKBOX(ctrl, ctrl.GetId(), self.OnFlipLR)
        gl_canvas.set_flip_lr(ctrl.IsChecked())

        ctrl = xrc.XRCCTRL(new_panel,"ROTATE180")
        self.widgets2canv[ctrl]=gl_canvas
        wx.EVT_CHECKBOX(ctrl, ctrl.GetId(), self.OnRotate180)
        gl_canvas.set_rotate_180(ctrl.IsChecked())

        ctrl = xrc.XRCCTRL(new_panel,"FULLCANVAS")
        self.widgets2canv[ctrl]=gl_canvas
        wx.EVT_CHECKBOX(ctrl, ctrl.GetId(), self.OnFullcanvas)
        gl_canvas.set_fullcanvas(ctrl.IsChecked())

        Color = xrc.XRCCTRL(new_panel,"COLOR")
        self.widgets2canv[Color]=gl_canvas
        Which = xrc.XRCCTRL(new_panel,"WHICH")
        self.widgets2canv[Which]=gl_canvas

        self.gl_canvases.append( (gl_canvas, Color, Which) )

        ni = numpy.random.uniform( 0, 255, SIZE).astype(numpy.uint8)
        pygim = ArrayInterfaceImage(ni,allow_copy=False)
        gl_canvas.new_image(pygim)

    def _event2canvas(self,event):
        widget = event.GetEventObject()
        gl_canvas = self.widgets2canv[widget]
        return gl_canvas

    def OnFlipLR(self,event):
        gl_canvas = self._event2canvas(event)
        gl_canvas.set_flip_lr(event.GetEventObject().IsChecked())

    def OnRotate180(self,event):
        gl_canvas = self._event2canvas(event)
        gl_canvas.set_rotate_180(event.GetEventObject().IsChecked())

    def OnFullcanvas(self,event):
        gl_canvas = self._event2canvas(event)
        gl_canvas.set_fullcanvas(event.GetEventObject().IsChecked())

    def OnTimer(self, event):
        for (gl_canvas,Color,Which) in self.gl_canvases:
            my_numpy_array = numpy.random.uniform( 0, 255, SIZE).astype(numpy.uint8)
            color = Color.GetStringSelection()
            if color==u'red':
                my_numpy_array[:,:,1:]=0 # make red
            elif color==u'multi':
                pass
            else:
                raise ValueError('')

            which = Which.GetStringSelection()
            if which==u'bottom':
                my_numpy_array[5:,:,:]=0 # make only bottom pixels displayed
            elif which==u'left':
                my_numpy_array[:,5:,:]=0 # make only bottom pixels displayed
            elif which==u'all':
                pass
            else:
                raise ValueError('')

            gl_canvas.update_image( my_numpy_array )
            gl_canvas.OnDraw()

def main():
    import os
    if int(os.environ.get('NO_REDIRECT','0')):
        kw = {}
    else:
	kw = dict(redirect=True,filename='demo.log')
    app = DemoApp(**kw)
    app.MainLoop()

if __name__=='__main__':
    main()

