# -*- coding: utf-8 -*-
"""
    sphinx.util.fileutil
    ~~~~~~~~~~~~~~~~~~~~

    File utility functions for Sphinx.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import os
import codecs
import posixpath
from docutils.utils import relative_path
from sphinx.util.osutil import copyfile, ensuredir, walk


def copy_asset_file(source, destination, context=None, renderer=None):
    """Copy an asset file to destination.

    On copying, it expands the template variables if context argument is given and
    the asset is a template file.

    :param source: The path to source file
    :param destination: The path to destination file or directory
    :param context: The template variables. If not given, template files are simply copied
    :param renderer: The template engine
    """
    if not os.path.exists(source):
        return

    if os.path.exists(destination) and os.path.isdir(destination):
        # Use source filename if destination points a directory
        destination = os.path.join(destination, os.path.basename(source))

    if source.lower().endswith('_t') and context:
        if renderer is None:
            msg = 'Template engine is not initialized. Failed to render %s' % source
            raise RuntimeError(msg)

        with codecs.open(source, 'r', encoding='utf-8') as fsrc:
            with codecs.open(destination[:-2], 'w', encoding='utf-8') as fdst:
                fdst.write(renderer.render_string(fsrc.read(), context))
    else:
        copyfile(source, destination)


def copy_asset(source, destination, excluded=lambda path: False, context=None, renderer=None):
    """Copy asset files to destination recursively.

    On copying, it expands the template variables if context argument is given and
    the asset is a template file.

    :param source: The path to source file or directory
    :param destination: The path to destination directory
    :param excluded: The matcher to determine the given path should be copied or not
    :param context: The template variables. If not given, template files are simply copied
    :param renderer: The template engine
    """
    if not os.path.exists(source):
        return

    ensuredir(destination)
    if os.path.isfile(source):
        copy_asset_file(source, destination, context, renderer)
        return

    for root, dirs, files in walk(source):
        reldir = relative_path(source, root)
        for dir in dirs[:]:
            if excluded(posixpath.join(reldir, dir)):
                dirs.remove(dir)
            else:
                ensuredir(posixpath.join(destination, reldir, dir))

        for filename in files:
            if not excluded(posixpath.join(reldir, filename)):
                copy_asset_file(posixpath.join(root, filename),
                                posixpath.join(destination, reldir),
                                context, renderer)