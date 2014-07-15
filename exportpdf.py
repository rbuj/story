# -*- coding: utf-8 -*-
#Copyright (c) 2011-14 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

import os
import time
import json

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from glib import GError
from gi.repository import Pango
from gi.repository import PangoCairo
import cairo

from gettext import gettext as _

import logging
_logger = logging.getLogger("story-activity")

LEFT_MARGIN = 50
TOP_MARGIN = 50

def save_pdf(activity, tmp_file, nick, description=None):
    ''' Output a PDF document from the title, pictures, and descriptions '''

    head = 18
    body = 12

    if activity._game.get_mode() == 'array':
        PAGE_WIDTH = 545
        PAGE_HEIGHT = 700
    else:
        PAGE_WIDTH = 700
        PAGE_HEIGHT = 545
    pdf_surface = cairo.PDFSurface(tmp_file, PAGE_WIDTH, PAGE_HEIGHT)

    fd = Pango.FontDescription('Sans')
    cr = cairo.Context(pdf_surface)
    cr.set_source_rgb(0, 0, 0)

    if activity._game.get_mode() == 'array':
        y = TOP_MARGIN * 3
    else:
        y = TOP_MARGIN

    show_text(cr, fd, activity.metadata['title'], head, LEFT_MARGIN, y,
              PAGE_WIDTH)
    y += 4 * head
    show_text(cr, fd, nick, body, LEFT_MARGIN, y, PAGE_WIDTH)
    y += head
    show_text(cr, fd, time.strftime('%x', time.localtime()), body,
              LEFT_MARGIN, y, PAGE_WIDTH)

    if activity._game.get_mode() == 'array':
        y += TOP_MARGIN * 3
    else:
        y += TOP_MARGIN * 2

    if description is not None:
        show_text(cr, fd, description, body, LEFT_MARGIN, y, PAGE_WIDTH)
    cr.show_page()

    if activity._game.get_mode() == 'array':
        text = ''
        if 'text' in activity.metadata:
            text = activity.metadata['text']
        one_page(activity, cr, fd, body, text, PAGE_WIDTH)
    else:
        save_page = activity._game.current_image
        for i in range(9):
            activity._game.current_image = i
            text = ''
            if 'text-%d' % i in activity.metadata:
                text = activity.metadata['text-%d' % i]
            page(activity, cr, fd, body, text, PAGE_WIDTH)
        activity._game.current_image = save_page


def one_page(activity, cr, fd, body, text, page_width):
    w = h = int((4 * activity._game._space + 3 * activity._game._dot_size))
    xo = int((page_width - (w / 2)) * 0.5)
    yo = TOP_MARGIN
    png_surface = activity._game.export()
    cr.save()
    cr.scale(0.67, 0.67)
    for i in range(9):
        y = activity._game._space + int(i / 3.) * \
            (activity._game._dot_size + activity._game._space)
        x = xo + activity._game._space + (i % 3) * \
            (activity._game._dot_size + activity._game._space)
        cr.save()
        cr.set_source_surface(activity._game._dots[i].images[0], x, y)
        cr.rectangle(x, y, activity._game._dot_size, activity._game._dot_size)
        cr.fill()
        cr.restore()
    cr.restore()

    show_text(cr, fd, text, body, LEFT_MARGIN, 350 + TOP_MARGIN, page_width)

    cr.show_page()


def page(activity, cr, fd, body, text, page_width):
    w = h = int((4 * activity._game._space + 3 * activity._game._dot_size))
    x = int((page_width - (w / 2)) * 0.67) + LEFT_MARGIN
    y = TOP_MARGIN
    png_surface = activity._game.export()
    cr.save()
    cr.scale(0.67, 0.67)
    cr.set_source_surface(
        activity._game._Dots[activity._game.current_image].images[0], x, y)
    cr.rectangle(x, y, w, h)
    cr.fill()
    cr.restore()

    show_text(cr, fd, text, body, LEFT_MARGIN, 350 + TOP_MARGIN, page_width)

    cr.show_page()


def show_text(cr, fd, label, size, x, y, page_width):
    pl = PangoCairo.create_layout(cr)
    fd.set_size(int(size * Pango.SCALE))
    pl.set_font_description(fd)
    if type(label) == str or type(label) == unicode:
        pl.set_text(label.replace('\0', ' '), -1)
    else:
        pl.set_text(str(label), -1)
    pl.set_width((page_width - LEFT_MARGIN * 2) * Pango.SCALE)
    cr.save()
    cr.translate(x, y)
    PangoCairo.update_layout(cr, pl)
    PangoCairo.show_layout(cr, pl)
    cr.restore()