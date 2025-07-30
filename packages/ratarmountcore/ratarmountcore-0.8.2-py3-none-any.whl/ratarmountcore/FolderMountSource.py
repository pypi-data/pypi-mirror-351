#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import stat
from typing import Any, Dict, IO, Iterable, Optional, Union

from .MountSource import FileInfo, MountSource
from .utils import overrides


def maxUpCount(path):
    if os.path.isabs(path):
        return 0
    result = 0
    upCount = 0
    for part in path.split(os.path.sep):
        if part == '..':
            upCount += 1
            result = max(result, upCount)
        elif part in ['.', '']:
            continue
        else:
            upCount -= 1
    return result


class FolderMountSource(MountSource):
    """
    This class manages one folder as mount source offering methods for listing folders, reading files, and others.
    """

    def __init__(self, path: str) -> None:
        self.root: str = path
        self._statfs = FolderMountSource._getStatfsForFolder(self.root)

    def setFolderDescriptor(self, fd: int) -> None:
        """
        Make this mount source manage the special "." folder by changing to that directory.
        Because we change to that directory it may only be used for one mount source but it also works
        when that mount source is mounted on!
        """
        os.fchdir(fd)
        self.root = '.'
        self._statfs = FolderMountSource._getStatfsForFolder(self.root)

    @staticmethod
    def _getStatfsForFolder(path: str):
        result = os.statvfs(path)
        return {
            'f_bsize': result.f_bsize,
            'f_frsize': result.f_frsize,
            'f_blocks': result.f_blocks,
            'f_bfree': 0,
            'f_bavail': 0,
            'f_files': result.f_files,
            'f_ffree': 0,
            'f_favail': 0,
            'f_namemax': result.f_namemax,
        }

    def _realpath(self, path: str) -> str:
        """Path given relative to folder root. Leading '/' is acceptable"""
        return os.path.join(self.root, path.lstrip(os.path.sep))

    @staticmethod
    def _statsToFileInfo(stats: os.stat_result, path: str, linkname: str):
        return FileInfo(
            # fmt: off
            size     = stats.st_size,
            mtime    = stats.st_mtime,
            mode     = stats.st_mode,
            linkname = linkname,
            uid      = stats.st_uid,
            gid      = stats.st_gid,
            userdata = [path],
            # fmt: on
        )

    @staticmethod
    def _dirEntryToFileInfo(dirEntry: os.DirEntry, path: str, realpath: str):
        try:
            linkname = os.readlink(realpath) if dirEntry.is_symlink() else ""
        except OSError:
            linkname = ""

        return FolderMountSource._statsToFileInfo(dirEntry.stat(follow_symlinks=False), linkname, path)

    @overrides(MountSource)
    def isImmutable(self) -> bool:
        return False

    @overrides(MountSource)
    def exists(self, path: str) -> bool:
        return os.path.lexists(self._realpath(path))

    @overrides(MountSource)
    def getFileInfo(self, path: str, fileVersion: int = 0) -> Optional[FileInfo]:
        """All returned file infos contain a file path string at the back of FileInfo.userdata."""

        # This is a bit of problematic design, however, the fileVersions count from 1 for the user.
        # And as -1 means the last version, 0 should also mean the first version ...
        # Basically, I did accidentally mix user-visible versions 1+ versions with API 0+ versions,
        # leading to this problematic clash of 0 and 1.
        if fileVersion not in [0, 1] or not self.exists(path):
            return None

        realpath = self._realpath(path)
        linkname = ""
        if os.path.islink(realpath):
            linkname = os.readlink(realpath)
            # Resolve relative links that point outside the source folder because they will become invalid
            # if they are mounted onto a different path. This relatively simply logic only works under the
            # assumption that "path" is normalized, i.e., it does not contain links in its path and no double
            # slashes and no '/./'. Calling os.path.normpath would remedy the latter but ONLY under the
            # assumption that there are no symbolic links in the path, else it might make things worse.
            if (
                not os.path.isabs(linkname)
                and maxUpCount(linkname) > path.strip('/').count('/')
                and os.path.exists(realpath)
            ):
                realpath = os.path.realpath(realpath)
                return self._statsToFileInfo(os.stat(realpath), realpath, "")
        return self._statsToFileInfo(os.lstat(realpath), path.lstrip('/'), linkname)

    @overrides(MountSource)
    def listDir(self, path: str) -> Optional[Union[Iterable[str], Dict[str, FileInfo]]]:
        realpath = self._realpath(path)
        if not os.path.isdir(realpath):
            return None

        return {
            os.fsdecode(dirEntry.name): FolderMountSource._dirEntryToFileInfo(dirEntry, path, realpath)
            for dirEntry in os.scandir(realpath)
        }

    @overrides(MountSource)
    def listDirModeOnly(self, path: str) -> Optional[Union[Iterable[str], Dict[str, int]]]:
        realpath = self._realpath(path)
        if not os.path.isdir(realpath):
            return None

        # https://docs.python.org/3/library/os.html#os.scandir
        # > All os.DirEntry methods may perform a system call, but is_dir() and is_file() usually
        # > only require a system call for symbolic links; os.DirEntry.stat() always requires a
        # > system call on Unix but only requires one for symbolic links on Windows.
        # Unfortunately, I am not sure whether it would be sufficient to build the file mode from these
        # two getters. For now, I'd say that all the esoteric stuff is simply not supported.
        def makeMode(dirEntry):
            mode = stat.S_IFDIR if dirEntry.is_dir(follow_symlinks=False) else stat.S_IFREG
            if dirEntry.is_symlink():
                mode = stat.S_IFLNK
            return mode

        return {os.fsdecode(dirEntry.name): makeMode(dirEntry) for dirEntry in os.scandir(realpath)}

    @overrides(MountSource)
    def fileVersions(self, path: str) -> int:
        return 1 if self.exists(path) else 0

    @overrides(MountSource)
    def open(self, fileInfo: FileInfo, buffering=-1) -> IO[bytes]:
        realpath = self.getFilePath(fileInfo)
        try:
            return open(realpath, 'rb', buffering=buffering)
        except Exception as e:
            raise ValueError(f"Specified path '{realpath}' is not a file that can be read!") from e

    @overrides(MountSource)
    def statfs(self) -> Dict[str, Any]:
        return self._statfs.copy()

    @overrides(MountSource)
    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass

    def getFilePath(self, fileInfo: FileInfo) -> str:
        path = fileInfo.userdata[-1]
        assert isinstance(path, str)
        # Path argument is only expected to be absolute for symbolic links pointing outside self.root.
        return path if path.startswith('/') else self._realpath(path)
