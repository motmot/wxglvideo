# $Id: wxglvideo.py 1156 2006-06-23 07:49:53Z astraw $
from __future__ import division
import math
import numpy as nx

import imops

import wx
import wx.glcanvas
import OpenGL.GL as gl
import warnings

class DynamicImageCanvas(wx.glcanvas.GLCanvas):
    def __init__(self, *args, **kw):
        wx.glcanvas.GLCanvas.__init__(*(self,)+args, **kw)
        self.init = False
        wx.EVT_ERASE_BACKGROUND(self, self.OnEraseBackground)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_PAINT(self, self.OnPaint)
        wx.EVT_IDLE(self, self.OnDraw)
        self._gl_tex_info_dict = {}
        self.do_clipping = False
        self.rotate_180 = False
        self.flip_LR = False
        self.lbrt = {}
        self.draw_points = {}
        self.reconstructed_points = {}
        self.extra_points_linesegs = {}
        self.do_draw_points = True
        self.x_border_pixels = 1
        self.y_border_pixels = 1
        self.minimum_eccentricity = 1.4

        # keep numpy from upcasting
        self.mask_high = nx.array(255,dtype=nx.uint8) 
        self.mask_low = nx.array(0,dtype=nx.uint8)

    def set_clipping(self, value):
        if value:
            warnings.warn('clipping disabled for performance reasons')
            return
        self.do_clipping = value

    def set_rotate_180(self, value):
        self.rotate_180 = value

    def set_flip_LR(self, value):
        self.flip_LR = value

    def get_clipping(self):
        return self.do_clipping

    def set_display_points(self, value):
        self.do_draw_points = value

    def get_display_points(self):
        return self.do_draw_points

    def delete_image(self,id_val):
        tex_id, gl_tex_xy_alloc, gl_tex_xyfrac, widthheight, internal_format, data_format = self._gl_tex_info_dict[id_val]
        glDeleteTextures( tex_id )
        del self._gl_tex_info_dict[id_val]

    def set_draw_points(self,id_val,points):
        self.draw_points[id_val]=points

    def set_reconstructed_points(self,id_val,points):
        self.reconstructed_points[id_val]=points

    def set_lbrt(self,id_val,lbrt):
        self.lbrt[id_val]=lbrt

    def __del__(self, *args, **kwargs):
        for id_val in self._gl_tex_info_dict.keys():
            self.delete_image(id_val)
            
    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW. (inhereted from wxDemo)

    def OnSize(self, event):
        size = self.GetClientSize()
        if self.GetContext():
            self.SetCurrent()
            glViewport(0, 0, size.width, size.height)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()
        
    def InitGL(self):
        self.gl_vendor = gl.glGetString(gl.GL_VENDOR)
        self.gl_renderer = gl.glGetString(gl.GL_RENDERER)
        self.gl_version = gl.glGetString(gl.GL_VERSION)
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0,1,0,1,-1,1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glEnable( gl.GL_BLEND )
        gl.glClearColor(0.0, 1.0, 0.0, 0.0) # green
        gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
        gl.glDisable(gl.GL_DEPTH_TEST);
        gl.glColor4f(1.0,1.0,1.0,1.0)
        gl.glEnable( gl.GL_POINT_SMOOTH )
        gl.glPointSize(5)
        
    def create_texture_object(self,id_val,image):
        def next_power_of_2(f):
            return int(math.pow(2.0,math.ceil(math.log(f)/math.log(2.0))))

        height, width = image.shape[:2]
        if len(image.shape) == 3:
            assert image.shape[2] == 3 # only support for RGB now...
            has_color = True
        else:
            has_color = False
        
        width_pow2  = next_power_of_2(width)
        height_pow2  = next_power_of_2(height)

        if not has_color:
            buffer = nx.zeros( (height_pow2,width_pow2,2), dtype=image.dtype )+128
            buffer[0:height,0:width,0] = image

            if self.do_clipping:
                clipped = nx.greater(image,254) + nx.less(image,1)
                mask = nx.choose(clipped, (self.mask_high, self.mask_low) )
                buffer[0:height,0:width,1] = mask
                raise RuntimeError('clipping should be disabled, how did we get here?')
                
            internal_format = gl.GL_LUMINANCE_ALPHA # keep alpha channel for clipping
            data_format = gl.GL_LUMINANCE
        else:
            buffer = nx.zeros( (height_pow2,width_pow2,image.shape[2]), dtype=image.dtype )
            buffer[0:height, 0:width, :] = image
            internal_format = gl.GL_RGB
            data_format = gl.GL_RGB

        raw_data = buffer.tostring()

        tex_id = gl.glGenTextures(1)

        gl_tex_xy_alloc = width_pow2, height_pow2
        gl_tex_xyfrac = width/float(width_pow2),  height/float(height_pow2)
        widthheight = width, height

        self._gl_tex_info_dict[id_val] = (tex_id, gl_tex_xy_alloc, gl_tex_xyfrac,
                                          widthheight, internal_format, data_format)

        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glTexEnvi(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, # target
                     0, #mipmap_level
                     internal_format,
                     width_pow2,
                     height_pow2,
                     0, #border,
                     data_format,
                     gl.GL_UNSIGNED_BYTE, #data_type,
                     raw_data)

    def update_image(self,
                     id_val,
                     image,
                     format='MONO8',
                     xoffset=0,
                     yoffset=0):
        image=nx.asarray(image)
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
        elif format == 'MONO16':
            image = imops.mono16_to_mono8_middle8bits( image )
        else:
            raise ValueError("Unknown format '%s'"%(format,))
        
        if id_val not in self._gl_tex_info_dict:
            self.create_texture_object(id_val,image)
            return
        height, width = image.shape[:2]
        tex_id, gl_tex_xy_alloc, gl_tex_xyfrac, widthheight, internal_format, data_format = self._gl_tex_info_dict[id_val]
        
        max_x, max_y = gl_tex_xy_alloc 
        if width > max_x or height > max_y: 
            self.delete_image(id_val) 
            self.create_texture_object(id_val,image)
        else:
            if len(image.shape) == 3:
                # color image
                this_data_format = gl.GL_RGB
                buffer_string = image.tostring()
            else:
                # XXX allocating new memory...
                if not hasattr(self,'_buffer') or self._buffer.shape != (height,width,2):
                    self._buffer = nx.zeros( (height,width,2), dtype=image.dtype )

                if self.do_clipping:
                    clipped = nx.greater(image,254).astype(nx.uint8) + nx.less(image,1).astype(nx.uint8)
                    mask = nx.choose(clipped, (255, 200) ).astype(nx.uint8) # alpha for transparency
                    self._buffer[:,:,0] = image
                    self._buffer[:,:,1] = mask
                    this_data_format = gl.GL_LUMINANCE_ALPHA
                    buffer_string = self._buffer.tostring()
                else:
                    this_data_format = gl.GL_LUMINANCE
                    buffer_string = image.tostring()
                    
            if this_data_format != data_format:
                raise ValueError('data format changed (old %s, new %s, GL_RGB %d, GL_LUMINANCE %d, GL_LUMINANCE_ALPHA %d)!'%(
                    data_format,this_data_format, gl.GL_RGB, gl.GL_LUMINANCE, gl.GL_LUMINANCE_ALPHA)) # probably wxgl.glvideo internal error
            
            self._gl_tex_xyfrac = width/float(max_x),  height/float(max_y)
            gl.glBindTexture(gl.GL_TEXTURE_2D,tex_id)
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, #target,
                            0, #mipmap_level,
                            xoffset, #x_offset,
                            yoffset, #y_offset,
                            width,
                            height,
                            this_data_format,
                            gl.GL_UNSIGNED_BYTE, #data_type,
                            buffer_string)
            self.extra_points_linesegs[id_val] = ([],[])
            
    def update_image_and_drawings(self,
                                  id_val,
                                  image,
                                  format='MONO8',
                                  points=None,
                                  linesegs=None,
                                  xoffset=0,
                                  yoffset=0):

        self.update_image( id_val,
                           image,
                           format=format,
                           xoffset=xoffset,
                           yoffset=yoffset)
        # draw points and linesegs
        if points is None:
            points = []
        if linesegs is None:
            linesegs = []
        self.extra_points_linesegs[id_val] = (points, linesegs)

    def OnDraw(self,*dummy_arg):
        N = len(self._gl_tex_info_dict)
        if N == 0:
            gl.glClearColor(0.0, 0.0, 0.0, 0.0) # black
            gl.glColor4f(0.0,1.0,0.0,1.0) # green
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_BLEND)
            gl.glRasterPos3f(.02,.02,0)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glEnable(gl.GL_BLEND)
            gl.glClearColor(0.0, 1.0, 0.0, 0.0) # green
            gl.glColor4f(1.0,1.0,1.0,1.0) # white
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            ids = self._gl_tex_info_dict.keys()
            ids.sort()
            size = self.GetClientSize()

            x_border = self.x_border_pixels/float(size[0])
            y_border = self.y_border_pixels/float(size[1])
            hx = x_border*0.5
            hy = y_border*0.5
            x_borders = x_border*(N+1)
            y_borders = y_border*(N+1)
            for i in range(N):
                bottom = y_border
                top = 1.0-y_border
                left = (1.0-2*hx)*i/float(N)+hx+hx
                right = (1.0-2*hx)*(i+1)/float(N)-hx+hx

                tex_id, gl_tex_xy_alloc, gl_tex_xyfrac, widthheight, internal_format, data_format = self._gl_tex_info_dict[ids[i]]

                xx,yy = gl_tex_xyfrac

                gl.glBindTexture(gl.GL_TEXTURE_2D,tex_id)
                if self.flip_LR:
                    left,right=right,left
                if not self.rotate_180:
                    gl.glBegin(gl.GL_QUADS)
                    gl.glTexCoord2f( 0, yy) # texture is flipped upside down to fix OpenGL<->na
                    gl.glVertex2f( left, bottom)

                    gl.glTexCoord2f( xx, yy)
                    gl.glVertex2f( right, bottom)

                    gl.glTexCoord2f( xx, 0)
                    gl.glVertex2f( right, top)

                    gl.glTexCoord2f( 0, 0)
                    gl.glVertex2f( left,top)
                    gl.glEnd()
                else:
                    gl.glBegin(gl.GL_QUADS)
                    gl.glTexCoord2f( xx, 0)
                    gl.glVertex2f( left, bottom)

                    gl.glTexCoord2f( 0, 0)
                    gl.glVertex2f( right, bottom)

                    gl.glTexCoord2f( 0, yy)
                    gl.glVertex2f( right, top)

                    gl.glTexCoord2f( xx, yy)
                    gl.glVertex2f( left,top)
                    gl.glEnd()

                xg=right-left
                xo=left
                yg=top-bottom
                yo=bottom
                
                width = float(widthheight[0])
                height = float(widthheight[1])

                points,linesegs = self.extra_points_linesegs.get(ids[i],([],[]))

                gl.glDisable(gl.GL_TEXTURE_2D)
                gl.glColor4f(0.0,1.0,0.0,1.0) # green point

                gl.glBegin(gl.GL_POINTS)
                for pt in points:
                    if self.rotate_180:
                        pt = width-pt[0], height-pt[1]
                    
                    x = pt[0]/width*xg+xo
                    y = (height-pt[1])/height*yg+yo
                    gl.glVertex2f(x,y)
                gl.glEnd()

                gl.glBegin(gl.GL_LINES)
                for L in linesegs:
                    if self.rotate_180:
                        L = width-L[0], height-L[1], width-L[2], height-L[3]
                    x0 = L[0]/width*xg+xo
                    y0 = (height-L[1])/height*yg+yo
                    x1 = L[2]/width*xg+xo
                    y1 = (height-L[3])/height*yg+yo
                    gl.glVertex2f(x0,y0)
                    gl.glVertex2f(x1,y1)
                gl.glEnd()

                gl.glColor4f(1.0,1.0,1.0,1.0)                        
                gl.glEnable(gl.GL_TEXTURE_2D)
                    
                if self.do_draw_points:
                    # draw points if needed
                    draw_points = self.draw_points.get(ids[i],[])
                    
                    gl.glDisable(gl.GL_TEXTURE_2D)
                    gl.glColor4f(0.0,1.0,0.0,1.0) # green point
                    gl.glBegin(gl.GL_POINTS)

                    for pt in draw_points:
                        if not pt[9]: # found_anything is false
                            continue
                        x = pt[0]/width*xg+xo
                        y = (height-pt[1])/height*yg+yo
                        gl.glVertex2f(x,y)
                        
                    gl.glEnd()
                    gl.glColor4f(1.0,1.0,1.0,1.0)                        
                    gl.glEnable(gl.GL_TEXTURE_2D)

                    for draw_point in draw_points:
                        found_anything = draw_point[9]
                        if not found_anything:
                            continue
                        
                        ox0,oy0,area,slope,eccentricity = draw_point[:5]
                        
                        if eccentricity <= self.minimum_eccentricity:
                            # don't draw green lines -- not much orientation info
                            continue
                        
                        xmin = 0
                        ymin = 0
                        xmax = width-1
                        ymax = height-1
                        
                        # ax+by+c=0
                        a=slope
                        b=-1
                        c=oy0-a*ox0
                        
                        x1=xmin
                        y1=-(c+a*x1)/b
                        if y1 < ymin:
                            y1 = ymin
                            x1 = -(c+b*y1)/a
                        elif y1 > ymax:
                            y1 = ymax
                            x1 = -(c+b*y1)/a

                        x2=xmax
                        y2=-(c+a*x2)/b
                        if y2 < ymin:
                            y2 = ymin
                            x2 = -(c+b*y2)/a
                        elif y2 > ymax:
                            y2 = ymax
                            x2 = -(c+b*y2)/a                

                        x1 = x1/width*xg+xo
                        x2 = x2/width*xg+xo

                        y1 = (height-y1)/height*yg+yo
                        y2 = (height-y2)/height*yg+yo

                        gl.glDisable(gl.GL_TEXTURE_2D)
                        gl.glColor4f(0.0,1.0,0.0,1.0) # green line
                        gl.glBegin(gl.GL_LINES)
                        gl.glVertex2f(x1,y1)
                        gl.glVertex2f(x2,y2)
                        gl.glEnd()
                        gl.glColor4f(1.0,1.0,1.0,1.0)                        
                        gl.glEnable(gl.GL_TEXTURE_2D)

                    # reconstructed points
                    draw_points, draw_lines = self.reconstructed_points.get(ids[i],([],[]))

                    # draw points
                    gl.glDisable(gl.GL_TEXTURE_2D)
                    gl.glColor4f(1.0,0.0,0.0,0.5) # red points
                    gl.glBegin(gl.GL_POINTS)

                    for pt in draw_points:
                        if pt[0] < 0 or pt[0] >= width or pt[1] < 0 or pt[1] >= height:
                            continue
                        x = pt[0]/width*xg+xo
                        y = (height-pt[1])/height*yg+yo
                        gl.glVertex2f(x,y)
                        
                    gl.glEnd()
                    gl.glColor4f(1.0,1.0,1.0,1.0)                        
                    gl.glEnable(gl.GL_TEXTURE_2D)

                    # draw lines

                    gl.glDisable(gl.GL_TEXTURE_2D)
                    gl.glColor4f(1.0,0.0,0.0,0.5) # red lines
                    gl.glBegin(gl.GL_LINES)

                    for L in draw_lines:
                        pt=[0,0]
                        a,b,c=L
                        # ax+by+c=0
                        # y = -(c+ax)/b
                        
                        # at x=0:
                        pt[0] = 0
                        pt[1] = -(c+a*pt[0])/b
                        
                        x = pt[0]/width*xg+xo
                        y = (height-pt[1])/height*yg+yo
                        gl.glVertex2f(x,y)

                        # at x=width-1:
                        pt[0] = width-1
                        pt[1] = -(c+a*pt[0])/b
                        
                        x = pt[0]/width*xg+xo
                        y = (height-pt[1])/height*yg+yo
                        gl.glVertex2f(x,y)

                    gl.glEnd()
                    gl.glColor4f(1.0,1.0,1.0,1.0)                        
                    gl.glEnable(gl.GL_TEXTURE_2D)

                if ids[i] in self.lbrt:
                    # draw ROI
                    l,b,r,t = self.lbrt[ids[i]]
                    if not self.rotate_180:
                        l = l/width*xg+xo
                        r = r/width*xg+xo
                        b = (height-b)/height*yg+yo
                        t = (height-t)/height*yg+yo
                    else:
                        l = (width-l)/width*xg+xo
                        r = (width-r)/width*xg+xo
                        b = b/height*yg+yo
                        t = t/height*yg+yo                        

                    eps = 1e-8
                    if (abs(r-l) + abs(t-b)) > (2-eps):
                        # don't draw ROI box if ROI is whole image
                        continue
                    gl.glDisable(gl.GL_TEXTURE_2D)
                    gl.glColor4f(0.0,1.0,0.0,1.0)
                    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                    gl.glBegin(gl.GL_QUADS)
                    gl.glVertex2f(l,b)
                    gl.glVertex2f(l,t)
                    gl.glVertex2f(r,t)
                    gl.glVertex2f(r,b)
                    gl.glEnd()
                    gl.glColor4f(1.0,1.0,1.0,1.0)
                    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                    gl.glEnable(gl.GL_TEXTURE_2D)
        
        self.SwapBuffers()
