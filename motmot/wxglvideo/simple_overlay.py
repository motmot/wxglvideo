import wx
import wx.xrc as xrc
import pkg_resources
import numpy
import motmot.imops.imops as imops
import pyglet.gl as gl
import warnings

from pygarrayimage.arrayimage import ArrayInterfaceImage

import motmot.wxglvideo.wxglvideo as vid

class PointDisplayCanvas( vid.DynamicImageCanvas ):
    def __init__(self,*args,**kw):
        self.extra_points_linesegs = None, None, None, None
        self.red_points = None
        super(PointDisplayCanvas, self).__init__(*args,**kw)

    def core_draw(self):
        super(PointDisplayCanvas, self).core_draw()

        points,point_colors, linesegs,lineseg_colors = self.extra_points_linesegs
        gl.glColor4f(0.0,1.0,0.0,1.0) # green point

        if points is not None:
            if point_colors is None:
                point_colors = [ (0,1,0,1) ] * len(points)
            gl.glBegin(gl.GL_POINTS)
            for color_4tuple,pt in zip(point_colors,points):
                gl.glColor4f(*color_4tuple)
                gl.glVertex2f(pt[0],pt[1])
            gl.glEnd()

        if linesegs is not None:
            if lineseg_colors is None:
                lineseg_colors = [ (0,1,0,1) ] * len(linesegs)
            for color_4tuple,this_lineseg in zip(lineseg_colors,linesegs):
                gl.glBegin(gl.GL_LINE_STRIP)
                gl.glColor4f(*color_4tuple)
                for (x,y) in zip(this_lineseg[0::2],this_lineseg[1::2]):
                    gl.glVertex2f(x,y)
                gl.glEnd()

        if self.red_points is not None:
            gl.glColor4f(1.0,0.0,0.0,0.5) # 50% alpha
            gl.glBegin(gl.GL_POINTS)
            for pt in self.red_points:
                gl.glVertex2f(pt[0],pt[1])
            gl.glEnd()

        gl.glColor4f(1.0,1.0,1.0,1.0) # restore white color

    def extra_initgl(self):
        gl.glEnable( gl.GL_POINT_SMOOTH )
        gl.glPointSize(5)

def copy_array_including_strides(arr):
    arr = numpy.asarray(arr)
    if arr.ndim!=2:
        raise NotImplementedError('only 2D arrays currently supported')
    newarr_full = numpy.empty( (arr.shape[0], arr.strides[0]), dtype=arr.dtype)
    newarr_full[:arr.shape[0],:arr.shape[1]]=arr
    newarr_view = newarr_full[:arr.shape[0],:arr.shape[1]]
    return newarr_view

class DynamicImageCanvas(wx.Panel):
    def __init__(self,*args,**kw):
        if 'child_kwargs' in kw:
            self.child_kwargs=kw['child_kwargs']
            del kw['child_kwargs']
        else:
            self.child_kwargs=None
        super(DynamicImageCanvas, self).__init__(*args,**kw)

        self.rotate_180 = False
        self.flip_lr = False

        self.children = {}
        self.children_full_roi_arr = {}
        self.lbrt = {}

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.box)
        #wx.EVT_IDLE( self, self.OnIdle )

    def _new_child(self,id_val,image,sort_add=False):
        self.Hide()
        try:
            if self.child_kwargs is None:
                kws = {}
            else:
                kws = self.child_kwargs
            child = PointDisplayCanvas(self,-1,**kws)
        finally:
            self.Show()
        child.set_fullcanvas(True)
        pygim = ArrayInterfaceImage( image, allow_copy=False )
        child.new_image( pygim )
        child.set_rotate_180( self.rotate_180 )
        child.set_flip_lr( self.flip_lr )

        self.children[id_val] = child
        self.lbrt[id_val] = ()

        id_vals = self.children.keys()
        id_vals.sort()

        if sort_add:
            # maintain ordering
            self.box = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.box)
            for id_val in id_vals:
                child = self.children[id_val]
                self.box.Add( child, 1, wx.EXPAND|wx.ALL, border=1)
        else:
            self.box.Add( child, 1, wx.EXPAND|wx.ALL, border=1)
        self.Layout()

    def set_rotate_180(self, value):
        self.rotate_180 = value
        for id_val in self.children:
            child = self.children[id_val]
            child.set_rotate_180(value)

    def set_flip_LR(self, value):
        self.flip_lr = value
        for id_val in self.children:
            child = self.children[id_val]
            child.set_flip_lr(value)

    def set_red_points(self,id_val,points):
        try:
            child = self.children[id_val]
        except KeyError:
            # XXX BUG: on the first frame for this camera, no points will be drawn
            pass
        else:
            child.red_points=points

    def set_lbrt(self,id_val,lbrt):
        self.lbrt[id_val]=lbrt

    def get_child_canvas(self, id_val):
        if id_val not in self.children:
            return None
        else:
            return self.children[id_val]

    def delete_image(self,id_val):
        child = self.children[id_val]
        child.DestroyChildren()
        child.Destroy()
        del self.children[id_val]
        self.Layout()
        if id_val in self.children_full_roi_arr:
            del self.children_full_roi_arr[id_val]

    def update_image(self, id_val, image, format='MONO8',
                     xoffset=0, yoffset=0, sort_add=False):
        image=numpy.asarray(image)
        if format == 'RGB8':
            image = imops.rgb8_to_rgb8( image )
        elif format == 'ARGB8':
            image = imops.argb8_to_rgb8( image )
        elif format == 'YUV411':
            image = imops.yuv411_to_rgb8( image )
        elif format == 'YUV422':
            image = imops.yuv422_to_rgb8( image )
        elif format == 'MONO8':
            pass
        elif format == 'RAW8':
            pass
        elif format == 'MONO16':
            image = imops.mono16_to_mono8_middle8bits( image )
        elif format.startswith('MONO8:'):
            warnings.warn('no Bayer do-mosaicing code implemented.')
            # pass through the raw Bayer mosaic
        else:
            raise ValueError("Unknown format '%s'"%(format,))

        if id_val not in self.children:
            self._new_child(id_val,image, sort_add=sort_add)
            self.children_full_roi_arr[id_val] = image
        else:
            child = self.children[id_val]
            previous_image = self.children_full_roi_arr[id_val]
            if not image.shape == previous_image.shape:
                fullh,fullw = previous_image.shape
                h,w = image.shape
                warnings.warn('use of ROI forces copy operation')
                # Current pyglet (v1.0) seems to assume width of image
                # to blit is width of full texture, so here we make a
                # full-size image rather than blitting the sub image.
                newim = copy_array_including_strides(previous_image)
                newim[yoffset:yoffset+h, xoffset:xoffset+w] = image
                image = newim
            self.children_full_roi_arr[id_val] = image
            child.update_image(image)

            #child.extra_points_linesegs = ([],[])

    def update_image_and_drawings(self,
                                  id_val,
                                  image,
                                  format='MONO8',
                                  points=None,
                                  point_colors=None,
                                  linesegs=None,
                                  lineseg_colors=None,
                                  xoffset=0,
                                  yoffset=0,
                                  sort_add=False):
        try:
            child = self.children[id_val]
        except KeyError:
            # XXX BUG: on the first frame for this camera, no points will be drawn
            pass
        else:
            child.extra_points_linesegs = (points, point_colors, linesegs, lineseg_colors)

        self.update_image( id_val,
                           image,
                           format=format,
                           xoffset=xoffset,
                           yoffset=yoffset,
                           sort_add=sort_add)


    def OnDraw(self):
        for id_val in self.children:
            child = self.children[id_val]
            child.OnDraw()

    def OnIdle(self, event):
        for id_val in self.children:
            child = self.children[id_val]
            child.OnDraw()
        event.RequestMore( True )
