************************************************************************************
:mod:`motmot.wxglvideo` -- CPU friendly display of uncompressed video using wxPython
************************************************************************************

.. module:: motmot.wxglvideo
  :synopsis: CPU friendly display of uncompressed video using wxPython
.. index::
   module: motmot.wxglvideo
   single: wxglvideo

The wxglvideo package allows rapid display of numpy arrays into
wxPython OpenGL contexts. In particular, it defines a class
:class:`~motmot.wxglvideo.wxglvideo.DynamicImageCanvas`, which is a
subclass of :class:`wx.glcanvas.GLCanvas` into which arrays are
blitted. By using the :mod:`pygarrayimage` module, it is possible to
enforce that no copy is made of the data on its way to OpenGL,
ensuring minimal resource use.

See also :mod:`motmot.wxvideo.wxvideo` for a similar module that does
not make use of OpenGL.

Screenshot of the :command:`wxglvideo_demo` program, included with
wxglvideo:

.. image:: _static/wxglvideo_demo_screenshot.png
  :alt: Screenshot of wxglvideo_demo

:mod:`motmot.wxglvideo.wxglvideo`
=================================

.. automodule:: motmot.wxglvideo.wxglvideo
   :members:
   :show-inheritance:


:mod:`motmot.wxglvideo.simple_overlay`
======================================

.. automodule:: motmot.wxglvideo.simple_overlay
   :members:
   :show-inheritance:

