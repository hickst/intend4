#
# Module to provide general file utility functions.
#   Written by: Tom Hicks. 1/29/2020.
#   Last Modified: Add get_permissions method.
#
import os
import shutil


def copy_tree (from_dir, to_dir):
  """
  Copy all files and subdirectories from the given source directory to
  the given target directory.
  """
  shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)


def filename_core (apath):
    """ Return the core filename string without the path prefix or extension. """
    if (apath is None):                     # sanity check
        return ''
    return os.path.basename(os.path.splitext(apath)[0])


def full_path (apath):
    """ Fully expand the given path into an absolute path. Supports the home ('~') shortcut. """
    return os.path.abspath(os.path.normpath(os.path.expanduser(apath)))


def gather_file_info (apath):
    """ Return a dictionary of common file information given a filepath. """
    file_info = dict()
    file_info['file_name'] = os.path.basename(apath)
    file_info['file_path'] = os.path.abspath(apath)
    file_info['file_size'] = os.path.getsize(apath)
    return file_info


def gen_file_paths (root_dir):
    """ Generator to yield all files in the file tree under the given root directory. """
    for root, dirs, files in os.walk(root_dir, followlinks=True):
        for fyl in files:
            file_path = os.path.join(root, fyl)
            yield file_path


def get_permissions(file_path):
  "Return the file OS status mode for the given filepath."
  return os.stat(file_path).st_mode


def good_dir_path (apath, writeable=False):
    """ Tell whether the given path points to a readable (and, optionally, writeable) directory
        or not. Follows symbolic links. """
    return (apath and os.path.isdir(apath) and
            is_readable(apath) and
            ((not writeable) or is_writable(apath)) )


def good_file_path (apath, writeable=False):
    """ Tell whether the given path points to a readable (and, optionally, writeable) file
        or not. Follows symbolic links. """
    return (apath and os.path.isfile(apath) and
            is_readable(apath) and
            ((not writeable) or is_writable(apath)) )


def is_acceptable_filename (filename, extents):
    """ Tell whether the given filename has one of the given set of accepatable
        file extensions or not. """
    if (filename is None):                  # sanity check
        return False
    return (filename.endswith(tuple(extents)))


def is_readable (apath):
    """ Tell whether given path points to a readable file or directory. Follows symbolic links. """
    return (apath and os.access(apath, os.R_OK))


def is_writable (apath):
    """ Tell whether given path points to a writable file or directory. Follows symbolic links. """
    return (apath and os.access(apath, os.W_OK))


def path_has_dots (apath):
    """ Tell whether the given path contains '.' or '..' """
    if (apath is None):                     # sanity check
        return False
    pieces = apath.split(os.sep)
    return (('.' in pieces) or ('..' in pieces))


def validate_file_path (apath, file_extents, writable=False):
    """ Tell whether the named file is acceptable and is readable (and writable). """
    return (is_acceptable_filename(apath, file_extents) and good_file_path(apath, writable))


def validate_path_strings (pathstrings, file_extents):
    """ Return a (possibly empty) list of valid file/directory paths. """
    path_list = []
    for pathname in pathstrings:
        if (validate_file_path(pathname, file_extents)):
            path_list.append(pathname)
        elif (good_dir_path(pathname)):
            path_list.append(pathname)
    return path_list
