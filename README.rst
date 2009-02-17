*****************************************************************************
:mod:`wxglvideo` -- CPU friendly display of uncompressed video using wxPython
*****************************************************************************

.. module:: wxglvideo
  :synopsis: CPU friendly display of uncompressed video using wxPython
.. index::
   module: wxglvideo
   single: wxglvideo

The wxglvideo package allows rapid display of numpy arrays into
wxPython OpenGL contexts. In particular, it defines a class
:class:`DynamicImageCanvas`, which is a subclass of
:class:`wx.glcanvas.GLCanvas` into which arrays are blitted. By using
the :mod:`pygarrayimage` module, it is possible to enforce that no
copy is made of the data on its way to OpenGL, ensuring minimal
resource use.

Screenshot of the :command:`wxglvideo_demo` program, included with
wxglvideo:

.. image:: _static/wxglvideo_demo_screenshot.png
  :alt: Screenshot of wxglvideo_demo
