"""
    Path auxiliary functions.
"""

__all__ = ['get_file_paths_in_dir', 'get_video_file_paths', 'get_image_file_paths', 'get_audio_file_paths',
           'get_json_file_paths', 'gen_output_file_path', 'gen_output_dir_path', 'check_rewrite_file_path',
           'gen_output_file_path_with_rewrite', 'gen_output_dir_path_with_rewrite']

import os
import re
import logging
import shutil


class FileExtChecker(object):
    """
    File extension checker.

    Parameters
    ----------
    exts : tuple(str, ...)
        File extensions.
    force_complex_ext : bool, default False
        Whether to forcibly treat extensions as complex ones.
    """
    def __init__(self,
                 exts: tuple[str, ...],
                 force_complex_ext: bool = False):
        super(FileExtChecker, self).__init__()
        self.exts = exts
        self.has_complex_ext = (force_complex_ext or
                                any([(len(ext) == 0) or (ext[0] != ".") or ("." in ext[1:]) for ext in exts]))

    def __call__(self, file_name: str) -> bool:
        """
        Process check request.

        Parameters
        ----------
        file_name : str
            File name.

        Returns
        -------
        bool
            Is the file extension the same.
        """
        if self.has_complex_ext:
            return any([file_name.endswith(ext) for ext in self.exts])
        else:
            _, file_ext = os.path.splitext(file_name)
            return file_ext.lower() in self.exts


def get_file_paths_in_dir(dir_path: str,
                          exts: tuple[str, ...],
                          explore_subdirs: bool,
                          return_dict: bool,
                          force_complex_ext: bool = False) -> list[str] | dict[str, str]:
    """
    Get all specific file paths in directory.

    Parameters
    ----------
    dir_path : str
        Path to working directory.
    exts : tuple(str, ...)
        Specific file extensions.
    explore_subdirs : bool
        Whether to explore subdirectories.
    return_dict : bool
        Whether to return dictionary structure.
    force_complex_ext : bool, default False
        Whether to forcibly treat extensions as complex ones.

    Returns
    -------
    list(str) or dict(str, str)
        Specific file paths.
    """
    ext_checker = FileExtChecker(exts, force_complex_ext)
    file_paths = {} if return_dict else []
    if explore_subdirs:
        for subdir, dirs, files in os.walk(dir_path):
            for file_name in files:
                if ext_checker(file_name):
                    if return_dict:
                        if subdir not in file_paths.keys():
                            file_paths[subdir] = []
                        file_paths[subdir].append(file_name)
                    else:
                        file_path = os.path.join(subdir, file_name)
                        file_paths.append(file_path)
    else:
        if return_dict:
            file_paths[dir_path] = []
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if not os.path.isfile(file_path):
                continue
            if ext_checker(file_name):
                if return_dict:
                    file_paths[dir_path].append(file_name)
                else:
                    file_paths.append(file_path)

    def sort_key(x: list) -> list:
        return [int(y) if y.isdigit() else y for y in re.findall(r"[^0-9]|[0-9]+", x)]

    if return_dict:
        file_paths = {k: sorted(file_paths[k], key=sort_key) for k in sorted(file_paths.keys(), key=sort_key)}
    else:
        file_paths = sorted(file_paths, key=sort_key)
    return file_paths


def get_video_file_paths(dir_path: str,
                         exts: tuple[str, ...] = (".mp4", ".mkv", ".avi", ".mov", ".m4v"),
                         explore_subdirs: bool = False,
                         return_dict: bool = False,
                         **kwargs) -> list[str] | dict[str, str]:
    """
    Get all video file paths in directory.

    Parameters
    ----------
    dir_path : str
        Path to working directory.
    exts : tuple(str, ...), default ('.mp4', '.mkv', '.avi', '.mov', '.m4v')
        Video file extensions.
    explore_subdirs : bool, default False
        Whether to explore subdirectories.
    return_dict : bool, default False
        Whether to return dictionary structure.

    Returns
    -------
    list(str) or dict(str, str)
        Video file paths.
    """
    return get_file_paths_in_dir(
        dir_path=dir_path,
        exts=exts,
        explore_subdirs=explore_subdirs,
        return_dict=return_dict,
        **kwargs)


def get_image_file_paths(dir_path: str,
                         exts: tuple[str, ...] = (".jpg", ".png"),
                         explore_subdirs: bool = False,
                         return_dict: bool = False,
                         **kwargs) -> list[str] | dict[str, str]:
    """
    Get all image file paths in directory.

    Parameters
    ----------
    dir_path : str
        Path to working directory.
    exts : tuple(str, ...), default ('.jpg', '.png')
        Image file extensions.
    explore_subdirs : bool, default False
        Whether to explore subdirectories.
    return_dict : bool, default False
        Whether to return dictionary structure.

    Returns
    -------
    list(str) or dict(str, str)
        Image file paths.
    """
    return get_file_paths_in_dir(
        dir_path=dir_path,
        exts=exts,
        explore_subdirs=explore_subdirs,
        return_dict=return_dict,
        **kwargs)


def get_audio_file_paths(dir_path: str,
                         exts: tuple[str, ...] = (".wav", ".mp3", "wma"),
                         explore_subdirs: bool = False,
                         return_dict: bool = False,
                         **kwargs) -> list[str] | dict[str, str]:
    """
    Get all audio file paths in directory.

    Parameters
    ----------
    dir_path : str
        Path to working directory.
    exts : tuple(str, ...), default ('.wav', '.mp3', 'wma')
        Audio file extensions.
    explore_subdirs : bool, default False
        Whether to explore subdirectories.
    return_dict : bool, default False
        Whether to return dictionary structure.

    Returns
    -------
    list(str) or dict(str, str)
        Audio file paths.
    """
    return get_file_paths_in_dir(
        dir_path=dir_path,
        exts=exts,
        explore_subdirs=explore_subdirs,
        return_dict=return_dict,
        **kwargs)


def get_json_file_paths(dir_path: str,
                        exts: tuple[str, ...] = (".json",),
                        explore_subdirs: bool = False,
                        return_dict: bool = False,
                        **kwargs) -> list[str] | dict[str, str]:
    """
    Get all JSON file paths in directory.

    Parameters
    ----------
    dir_path : str
        Path to working directory.
    exts : tuple(str, ...), default ('.json',)
        JSON file extensions.
    explore_subdirs : bool, default False
        Whether to explore subdirectories.
    return_dict : bool, default False
        Whether to return dictionary structure.

    Returns
    -------
    list(str) or dict(str, str)
        Audio file paths.
    """
    return get_file_paths_in_dir(
        dir_path=dir_path,
        exts=exts,
        explore_subdirs=explore_subdirs,
        return_dict=return_dict,
        **kwargs)


def gen_output_file_path(input_file_path: str,
                         output_dir_path: str,
                         output_file_ext: str | None = None,
                         output_file_suf: str = "",
                         input_file_suf_len: int = 0,
                         is_output_dir: bool = False) -> str:
    """
    Generate output file/directory path based on input file path.

    Parameters
    ----------
    input_file_path : str
        Input file path.
    output_dir_path : str
        Output directory path.
    output_file_ext : str or None, default None
        Output file extension with leading dot. `None` value means to keep existing file extension.
    output_file_suf : str, default ''
        Output file extra suffix with leading symbol like `_`.
    input_file_suf_len : int, default 0
        Removed input file suffix length (suffix with leading symbol like `_`).
    is_output_dir : bool, default False
        Whether to generate directory path.

    Returns
    -------
    str
        Output file/directory path.
    """
    input_file_name_stem, input_file_ext = os.path.splitext(os.path.basename(input_file_path))
    if input_file_suf_len > 0:
        input_file_name_stem = input_file_name_stem[:-input_file_suf_len]
    if is_output_dir:
        output_file_name = "{stem}{suf}".format(
            stem=input_file_name_stem,
            suf=output_file_suf)
    else:
        if output_file_ext is None:
            output_file_ext = input_file_ext
        output_file_name = "{stem}{suf}{ext}".format(
            stem=input_file_name_stem,
            suf=output_file_suf,
            ext=output_file_ext)
    output_file_path = os.path.join(output_dir_path, output_file_name)
    return output_file_path


def gen_output_dir_path(input_file_path: str,
                        output_base_dir_path: str,
                        output_dir_suf: str,
                        input_file_suf_len: int = 0) -> str:
    """
    Generate output directory path based on input file path.

    Parameters
    ----------
    input_file_path : str
        Input file path.
    output_base_dir_path : str
        Output base directory path.
    output_dir_suf : str
        Output directory extra suffix with leading symbol like `_`.
    input_file_suf_len : int, default 0
        Removed input file suffix length (suffix with leading symbol like `_`).

    Returns
    -------
    str
        Output directory path.
    """
    output_dir_path = gen_output_file_path(
        input_file_path=input_file_path,
        output_dir_path=output_base_dir_path,
        output_file_suf=output_dir_suf,
        input_file_suf_len=input_file_suf_len,
        is_output_dir=True)
    return output_dir_path


def check_rewrite_file_path(file_path: str,
                            rewrite: bool,
                            show_message: bool = True,
                            is_dir: bool = False) -> bool:
    """
    Check file/directory for non-existence.

    Parameters
    ----------
    file_path : str
        File/directory path.
    rewrite : bool
        Should we rewrite existing file/directory.
    show_message : bool
        Whether to show a skip message.
    is_dir : bool, default False
        Whether the object being evaluated is a directory.

    Returns
    -------
    bool
        Should we skip file processing.
    """
    if os.path.exists(file_path):
        if not rewrite:
            if show_message:
                obj_type_name = "Directory" if is_dir else "File"
                logging.info("{obj_type_name} `{file_path}` is already exist, skipped".format(
                    obj_type_name=obj_type_name,
                    file_path=file_path))
            return True
        else:
            if is_dir:
                shutil.rmtree(path=file_path)
            else:
                os.remove(file_path)
    if is_dir:
        os.mkdir(file_path)
    return False


def gen_output_file_path_with_rewrite(input_file_path: str,
                                      output_dir_path: str,
                                      output_file_ext: str | None = None,
                                      output_file_suf: str = "",
                                      input_file_suf_len: int = 0,
                                      is_output_dir: bool = False,
                                      rewrite: bool = False,
                                      show_message: bool = True) -> tuple[str, bool]:
    """
    Generate output file/directory path based on input file path. And check file/directory for non-existence.

    Parameters
    ----------
    input_file_path : str
        Input file path.
    output_dir_path : str
        Output directory path.
    output_file_ext : str or None, default None
        Output file extension with leading dot. `None` value means to keep existing file extension.
    output_file_suf : str, default ''
        Output file extra suffix with leading symbol like `_`.
    input_file_suf_len : int, default 0
        Removed input file suffix length (suffix with leading symbol like `_`).
    is_output_dir : bool, default False
        Whether to generate directory path.
    rewrite : bool, default False
        Should we rewrite existing file/directory.
    show_message : bool
        Whether to show a skip message.

    Returns
    -------
    str
        Output file/directory path.
    bool
        Should we skip file/directory processing.
    """
    output_file_path = gen_output_file_path(
        input_file_path=input_file_path,
        output_dir_path=output_dir_path,
        output_file_ext=output_file_ext,
        output_file_suf=output_file_suf,
        input_file_suf_len=input_file_suf_len,
        is_output_dir=is_output_dir)
    skip = check_rewrite_file_path(
        file_path=output_file_path,
        rewrite=rewrite,
        show_message=show_message,
        is_dir=is_output_dir)
    return output_file_path, skip


def gen_output_dir_path_with_rewrite(input_file_path: str,
                                     output_base_dir_path: str,
                                     output_dir_suf: str,
                                     input_file_suf_len: int = 0,
                                     rewrite: bool = False,
                                     show_message: bool = True) -> tuple[str, bool]:
    """
    Generate output directory path based on input file path. And check directory for non-existence.

    Parameters
    ----------
    input_file_path : str
        Input file path.
    output_base_dir_path : str
        Output base directory path.
    output_dir_suf : str
        Output directory extra suffix with leading symbol like `_`.
    input_file_suf_len : int, default 0
        Removed input file suffix length (suffix with leading symbol like `_`).
    rewrite : bool, default False
        Should we rewrite existing file/directory.
    show_message : bool
        Whether to show a skip message.

    Returns
    -------
    str
        Output directory path.
    bool
        Should we skip directory processing.
    """
    output_dir_path = gen_output_file_path(
        input_file_path=input_file_path,
        output_dir_path=output_base_dir_path,
        output_file_suf=output_dir_suf,
        input_file_suf_len=input_file_suf_len,
        is_output_dir=True)
    skip = check_rewrite_file_path(
        file_path=output_dir_path,
        rewrite=rewrite,
        show_message=show_message,
        is_dir=True)
    return output_dir_path, skip
