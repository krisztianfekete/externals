# coding: utf8
import unittest
import os
from temp_dir import in_temp_dir, within_temp_dir
import externals.fspath as m


class TestFsPath(unittest.TestCase):

    def test_parent_of_root_exception(self):
        x = m.FsPath(u'/')
        with self.assertRaises(m.NoParentError):
            x.parent()

    def test_child_of_root_has_a_parent(self):
        x = m.FsPath(u'/')
        child = x.child(u'stem')
        child.parent()

    def test_this_file_exists(self):
        x = m.FsPath(__file__)
        self.assertTrue(x.exists())

    def test_nonexistent_sibling_does_not_exists(self):
        x = m.FsPath(__file__).parent().child('nonexistent')
        self.assertFalse(x.exists())

    def test_this_file_is_a_file(self):
        x = m.FsPath(__file__)
        self.assertTrue(x.is_file())

    def test_this_file_is_not_a_directory(self):
        x = m.FsPath(__file__)
        self.assertFalse(x.is_dir())

    def test_root_is_not_a_file(self):
        x = m.FsPath(u'/')
        self.assertFalse(x.is_file())

    def test_root_is_a_directory(self):
        x = m.FsPath(u'/')
        self.assertTrue(x.is_dir())

    def test_name_is_last_segment_of_path(self):
        x = m.FsPath(u'/a/last')
        self.assertEqual(u'last', x.name)

    @within_temp_dir
    def test_content_returns_file_content(self):
            filename = u'test-file1'
            with open(filename, u'wb') as f:
                f.write('something\nand more')

            x = m.FsPath(filename)

            self.assertEqual('something\nand more', x.content())

    @within_temp_dir
    def test_set_content_stores_data(self):
            filename = u'test-file2'

            x_store = m.FsPath(filename)
            x_store.set_content('something2\nand more')

            x_read = m.FsPath(filename)
            self.assertEqual('something2\nand more', x_read.content())

    @within_temp_dir
    def test_readable_stream_returns_an_open_file(self):
            filename = u'test-file3'

            x_store = m.FsPath(filename)
            x_store.set_content('something3')

            x_read = m.FsPath(filename)
            with x_read.readable_stream() as stream:
                self.assertEqual('s', stream.read(1))
                self.assertEqual('o', stream.read(1))
                self.assertEqual('mething3', stream.read())

    @within_temp_dir
    def test_writable_stream_returns_an_open_file(self):
            x_tempdir = m.working_directory()

            x_store = x_tempdir.child(u'test-file')
            with x_store.writable_stream() as stream:
                stream.write('s')
                stream.write('o')
                stream.write('mething4')

            x_read = x_tempdir.child(u'test-file')
            self.assertEqual('something4', x_read.content())

    @within_temp_dir
    def test_children_returns_list_of_externals_for_children(self):
            x_tempdir = m.working_directory()
            x_tempdir.child(u'a').create('a content')
            x_tempdir.child(u'b').create('b content')
            os.mkdir('c')

            x_test = m.working_directory()

            def name(x):
                return x.name
            children = sorted(x_test.children(), key=name)

            self.assertEqual(3, len(children))
            self.assertEqual([u'a', u'b', u'c'], map(name, children))

    @within_temp_dir
    def test_external_is_an_iterable_of_its_children(self):
            x_tempdir = m.working_directory()
            x_tempdir.child(u'a').create('a content')
            x_tempdir.child(u'b').create('b content')
            os.mkdir('c')

            x_test = m.working_directory()
            children_list = []
            # iterate over the external
            for child in x_test:
                children_list.append(child)

            def name(x):
                return x.name
            children = sorted(x_test.children(), key=name)

            self.assertEqual(3, len(children))
            self.assertEqual([u'a', u'b', u'c'], map(name, children))

    @within_temp_dir
    def test_create_creates_missing_directories_and_a_file(self):
            x_tempdir = m.working_directory()
            x_a = x_tempdir.child(u'a')
            x_ab = x_a.child(u'b')
            x_file = x_ab.child(u'c')

            x_file.create('content')

            with open(u'a/b/c') as f:
                self.assertEqual('content', f.read())

    @within_temp_dir
    def test_directory_with_subdir_is_removed(self):
            x_tempdir = m.working_directory()
            x_a = x_tempdir.child(u'a')
            x_ab = x_a.child(u'b')
            x_file = x_ab.child(u'c')

            x_file.create('content')

            x_a.remove()

            self.assertFalse(x_ab.exists())

    @within_temp_dir
    def test_adding_a_string_to_an_external_means_asking_for_a_child(self):
            x_tempdir = m.working_directory()
            x_tempdir.child(u'a').create('child')

            self.assertEqual('child', (x_tempdir / u'a').content())

    @within_temp_dir
    def test_add_a_path(self):
            x_tempdir = m.working_directory()
            # file dir-a/dir-b/file
            (x_tempdir
                .child(u'dir-a')
                .child(u'dir-b')
                .child(u'file')).create('child')

            self.assertEqual(
                'child',
                (x_tempdir / u'dir-a/dir-b/file').content())

    @within_temp_dir
    def test_add_a_path_wrapped_in_slashes(self):
            x_tempdir = m.working_directory()
            # file dir-a/dir-b/file
            (x_tempdir
                .child(u'dir-a')
                .child(u'dir-b')
                .child(u'file')).create('child')

            self.assertEqual(
                'child',
                (x_tempdir / u'/dir-a/dir-b/file/').content())


class Test_working_directory(unittest.TestCase):

    def test_working_directory_is_an_fspath(self):
        self.assertIsInstance(m.working_directory(), m.FsPath)

    def test_working_directory_is_absolute(self):
        with in_temp_dir():
            x1 = m.working_directory()
            with in_temp_dir():
                x2 = m.working_directory()
                self.assertNotEqual(x1._path, x2._path)