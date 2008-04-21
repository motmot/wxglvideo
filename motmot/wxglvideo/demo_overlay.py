"""
Demonstrate the use of motmot.wxglvideo.simple_overlay.
"""

import pkg_resources
import numpy
import wx
import motmot.wxglvideo.demo as demo
import motmot.wxglvideo.simple_overlay as simple_overlay

SIZE=(240,320)

class DemoOverlapApp( demo.DemoApp ):
    def OnAddDisplay(self,event):
        if not hasattr(self, 'overlay_canvas'):
            self.main_panel = wx.Panel( self.target_panel )
            self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            self.main_panel.SetSizer(self.main_panel_sizer)
            self.target_box.Add(  self.main_panel, 1, wx.EXPAND )

            self.overlay_canvas = simple_overlay.DynamicImageCanvas(self.main_panel)
            self.main_panel_sizer.Add(  self.overlay_canvas, 1, wx.EXPAND )

            self.horiz_panel = wx.Panel( self.main_panel )
            self.horiz_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.horiz_panel.SetSizer(self.horiz_panel_sizer)
            self.main_panel_sizer.Add(  self.horiz_panel, 0, wx.EXPAND )

            self.target_panel.Layout()
            self.count = 0
            self.id_vals = []
            self.widgets = {}

        self.count += 1
        ni = numpy.random.uniform( 0, 255, SIZE).astype(numpy.uint8)
        id_val = 'id %d'%self.count

        if 1:
            ctrl = wx.StaticText( self.horiz_panel, label=id_val)
            self.horiz_panel_sizer.Add(  ctrl, wx.LEFT, border=5 )

            btn = wx.Button(self.horiz_panel, -1, "close")
            btn.id_val = id_val # store data in wx object
            wx.EVT_BUTTON(btn, btn.GetId(), self.OnCloseView)
            self.horiz_panel_sizer.Add(  btn, 0, wx.RIGHT, border=5 )
            self.widgets[id_val] = [ctrl, btn]

        self.overlay_canvas.update_image(id_val, ni)
        self.id_vals.append( id_val )
        
        self.target_panel.Layout()

    def OnTimer(self, event):
        if hasattr(self,'id_vals'):
            points = [ (10,10) ]
            linesegs = [ (20,10, 20,30) ]
            for id_val in self.id_vals:
                ni = numpy.random.uniform( 0, 255, SIZE).astype(numpy.uint8)
                self.overlay_canvas.update_image_and_drawings(id_val, ni, 
                                                              points=points,
                                                              linesegs=linesegs,
                                                              )

    def OnCloseView(self, event):
        widget = event.GetEventObject()
        id_val = widget.id_val # retrieve id value
        idx = self.id_vals.index(id_val)
        del self.id_vals[idx]
        self.overlay_canvas.delete_image(id_val)
        for widget in self.widgets[id_val]:
            self.horiz_panel_sizer.Remove( widget )
            widget.Destroy()
            self.horiz_panel_sizer.Layout()
def main():
    import os
    if int(os.environ.get('NO_REDIRECT','0')):
        kw = {}
    else:
	kw = dict(redirect=True,filename='demo.log')
    app = DemoOverlapApp(**kw)
    app.MainLoop()

if __name__=='__main__':
    main()
