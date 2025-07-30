#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=wrong-import-position
# pylint: disable=redefined-outer-name

import dataclasses
import io
import os
import sys
import tarfile
from typing import Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest  # noqa: E402

from ratarmountcore import FolderMountSource, SQLiteIndexedTar, UnionMountSource  # noqa: E402


@dataclasses.dataclass
class SampleArchive:
    path: str
    folders: List[str]
    files: Dict[str, bytes]


def _createFile(tarArchive, name, contents):
    tinfo = tarfile.TarInfo(name)
    tinfo.size = len(contents)
    tarArchive.addfile(tinfo, io.BytesIO(contents if isinstance(contents, bytes) else contents.encode()))


def _makeFolder(tarArchive, name):
    tinfo = tarfile.TarInfo(name)
    tinfo.type = tarfile.DIRTYPE
    tarArchive.addfile(tinfo, io.BytesIO())


def _populate_folder(sampleArchive: SampleArchive):
    for folder in sampleArchive.folders:
        os.makedirs(os.path.join(sampleArchive.path, folder.strip('/')), exist_ok=True)
    for path, contents in sampleArchive.files.items():
        with open(os.path.join(sampleArchive.path, path.strip('/')), "wb") as file:
            file.write(contents)


def _populate_tar(sampleArchive: SampleArchive):
    with tarfile.open(name=sampleArchive.path, mode="w:bz2") as tarFile:
        for folder in sampleArchive.folders:
            _makeFolder(tarFile, folder)
        for path, contents in sampleArchive.files.items():
            _createFile(tarFile, path, contents)


@pytest.fixture(name="sample_folder_a")
def fixture_sample_folder_a(tmpdir):
    sampleArchive = SampleArchive(
        # original tmpdir is a deprecated py.path.local object
        path=os.path.join(tmpdir.realpath(), "folderA"),
        folders=["subfolder"],
        files={"/subfolder/world": b"hello\n", "/ufo": b"iriya in folder 1\n"},
    )
    _populate_folder(sampleArchive)
    return sampleArchive


@pytest.fixture(name="sample_folder_b")
def fixture_sample_folder_b(tmpdir):
    sampleArchive = SampleArchive(
        # original tmpdir is a deprecated py.path.local object
        path=os.path.join(tmpdir.realpath(), "folderB"),
        folders=["subfolder"],
        files={"/ufo": b"iriya\n"},
    )
    _populate_folder(sampleArchive)
    return sampleArchive


@pytest.fixture(name="sample_tar_a")
def fixture_sample_tar_a(tmpdir):
    sampleArchive = SampleArchive(
        path=os.path.join(tmpdir.realpath(), "sampleA.tar"),
        folders=["subfolder"],
        files={"/ufo": b"inside", "/README.md": b"readme inside", "/subfolder/world": b"HELLO"},
    )
    _populate_tar(sampleArchive)
    return sampleArchive


@pytest.fixture(name="sample_tar_b")
def fixture_sample_tar_b(tmpdir):
    sampleArchive = SampleArchive(
        path=os.path.join(tmpdir.realpath(), "sampleB.tar"),
        folders=["/src", "/dist", "/dist/a", "/dist/a/b"],
        files={"/README.md": b"hello world", "/src/test.sh": b"echo hi", "/dist/a/b/test2.sh": "echo two"},
    )
    _populate_tar(sampleArchive)
    return sampleArchive


class TestUnionMountSource:
    @staticmethod
    def _check_file(mountSource, path, version, contents=None):
        fileInfo = mountSource.getFileInfo(path, version)
        assert fileInfo is not None
        if contents is not None:
            # The MountSource interface only allows to open files in binary mode, which returns bytes not string.
            if isinstance(contents, str):
                contents = contents.encode()
            with mountSource.open(fileInfo) as file:
                assert file.read() == contents

    @staticmethod
    def test_unite_two_folders(sample_folder_a, sample_folder_b):
        union = UnionMountSource([FolderMountSource(sample_folder_a.path), FolderMountSource(sample_folder_b.path)])
        for path in sample_folder_a.folders + sample_folder_b.folders:
            TestUnionMountSource._check_file(union, path, 0, None)
        for path, contents in sample_folder_b.files.items():
            TestUnionMountSource._check_file(union, path, 0, contents)
        for path, contents in sample_folder_a.files.items():
            TestUnionMountSource._check_file(union, path, 0 if path not in sample_folder_b.files else 1, contents)

    @staticmethod
    def test_unite_two_folders_and_update_one(sample_folder_a, sample_folder_b):
        union = UnionMountSource([FolderMountSource(sample_folder_a.path), FolderMountSource(sample_folder_b.path)])

        contents = b"atarashii iriya\n"
        with open(os.path.join(sample_folder_a.path, "ufo2"), "wb") as file:
            file.write(contents)
        os.mkdir(os.path.join(sample_folder_a.path, "subfolder2"))
        with open(os.path.join(sample_folder_a.path, "subfolder2/world"), "wb") as file:
            file.write(contents)
        os.mkdir(os.path.join(sample_folder_a.path, "subfolder3"))
        with open(os.path.join(sample_folder_a.path, "subfolder3/world"), "wb") as file:
            file.write(contents)
        with open(os.path.join(sample_folder_a.path, "second-world"), "wb") as file:
            file.write(contents)

        TestUnionMountSource._check_file(union, "/ufo2", 0, contents)
        TestUnionMountSource._check_file(union, "/subfolder2", 0, None)
        TestUnionMountSource._check_file(union, "/subfolder2/world", 0, contents)
        TestUnionMountSource._check_file(union, "/subfolder3/world", 0, contents)
        TestUnionMountSource._check_file(union, "/second-world", 0, contents)

    @staticmethod
    def test_unite_two_archives(sample_tar_a, sample_tar_b):
        union = UnionMountSource([SQLiteIndexedTar(sample_tar_a.path), SQLiteIndexedTar(sample_tar_b.path)])
        for path in sample_tar_a.folders + sample_tar_b.folders:
            TestUnionMountSource._check_file(union, path, 0, None)
        for path, contents in sample_tar_b.files.items():
            TestUnionMountSource._check_file(union, path, 0, contents)
        for path, contents in sample_tar_a.files.items():
            TestUnionMountSource._check_file(union, path, 0 if path not in sample_tar_b.files else 1, contents)

    @staticmethod
    def test_unite_folder_and_archive_and_update_folder(sample_tar_a, sample_folder_a):
        union = UnionMountSource([SQLiteIndexedTar(sample_tar_a.path), FolderMountSource(sample_folder_a.path)])
        for path in sample_tar_a.folders + sample_folder_a.folders:
            TestUnionMountSource._check_file(union, path, 0, None)
        for path, contents in sample_folder_a.files.items():
            TestUnionMountSource._check_file(union, path, 0, contents)
        for path, contents in sample_tar_a.files.items():
            print("patH:", path)
            TestUnionMountSource._check_file(union, path, 0 if path not in sample_folder_a.files else 1, contents)

        contents = b"atarashii iriya\n"
        with open(os.path.join(sample_folder_a.path, "ufo2"), "wb") as file:
            file.write(contents)
        os.mkdir(os.path.join(sample_folder_a.path, "subfolder2"))
        with open(os.path.join(sample_folder_a.path, "subfolder2/world"), "wb") as file:
            file.write(contents)
        os.mkdir(os.path.join(sample_folder_a.path, "subfolder3"))
        with open(os.path.join(sample_folder_a.path, "subfolder3/world"), "wb") as file:
            file.write(contents)

        TestUnionMountSource._check_file(union, "/ufo2", 0, contents)
        TestUnionMountSource._check_file(union, "/subfolder2", 0, None)
        TestUnionMountSource._check_file(union, "/subfolder2/world", 0, contents)
        TestUnionMountSource._check_file(union, "/subfolder3/world", 0, contents)
