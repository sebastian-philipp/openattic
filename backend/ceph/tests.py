# kate: space-indent on; indent-width 4; replace-tabs on;

"""
 *  Copyright (C) 2011-2016, it-novum GmbH <community@openattic.org>
 *
 *  openATTIC is free software; you can redistribute it and/or modify it
 *  under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; version 2.
 *
 *  This package is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
"""

import os
import mock
import tempfile
import json

from django.test import TestCase

import ceph.models
import ceph.librados

from ceph.librados import Keyring, undoable, undo_transaction


def open_testdata(name):
    return open(os.path.join(os.path.dirname(__file__), name))


class ClusterTestCase(TestCase):
    def test_get_recommended_pg_num(self):
        with mock.patch("ceph.models.Cluster.osd_set") as mock_osd_set:
            c = ceph.models.Cluster()
            # small setups
            mock_osd_set.count.return_value = 2
            self.assertEqual(c.get_recommended_pg_num(3), 128)
            mock_osd_set.count.return_value = 3
            self.assertEqual(c.get_recommended_pg_num(3), 128)

            # the example from the Ceph docs
            mock_osd_set.count.return_value = 200
            self.assertEqual(c.get_recommended_pg_num(3), 8192)

            # make sure the rounding step doesn't round up a power of two to
            # the next power of two above it, but keeps it unaltered
            mock_osd_set.count.return_value = 8192
            self.assertEqual(c.get_recommended_pg_num(100), 8192)


class KeyringTestCase(TestCase):
    def test_keyring_succeeds(self):
        with tempfile.NamedTemporaryFile(dir='/tmp', prefix='ceph.client.', suffix=".keyring") as tmpfile:
            tmpfile.write("[client.admin]")
            tmpfile.flush()
            keyring = Keyring('ceph', '/tmp')
            self.assertEqual(keyring.username, 'client.admin')

    def test_keyring_raises_runtime_error(self):
        try:
            keyring = Keyring('ceph', '/tmp')
        except RuntimeError, e:
            return True

    def test_username_raises_runtime_error(self):
        with tempfile.NamedTemporaryFile(dir='/tmp', prefix='ceph.client.', suffix=".keyring") as tmpfile:
            tmpfile.write("abcdef")
            tmpfile.flush()
            try:
                keyring = Keyring('ceph', '/tmp')
            except RuntimeError, e:
                return True


class CephPoolTestCase(TestCase):
    @mock.patch('ceph.models.CephPool.objects')
    @mock.patch('ceph.models.rados')
    @mock.patch('ceph.models.MonApi', autospec=True)
    def test_insert(self, monApi_mock, rados_mock, cephpool_objects_mock):
        cephpool_objects_mock.nodb_context = mock.Mock(fsid='hallo')
        cephpool_objects_mock.get.return_value = ceph.models.CephPool(id=0, name='test', pg_num=0, type='replicated')

        # Inserting new pool.
        pool = ceph.models.CephPool(name='test', pg_num=0, type='replicated')
        pool.save()
        monApi_mock.return_value.osd_pool_create.assert_called_with(pool='test', pg_num=0, pgp_num=0,
                                                                    pool_type='replicated', erasure_code_profile=None)
        cephpool_objects_mock.get.assert_called_with(name='test')
        self.assertFalse(pool._state.adding)

        # Modifying existing pool.
        pool = ceph.models.CephPool(id=0, name='test', pg_num=1, type='replicated')
        pool.save()
        calls = [mock.call(pool='test', var='pg_num', val=1),
                 mock.call(pool='test', var='pgp_num', val=1)]
        monApi_mock.return_value.osd_pool_set.assert_has_calls(calls)

        # Creating a pool tier.
        # FIXME: as get() returns pool with id=0, we cannot really use a different pool here.
        monApi_mock.return_value.osd_pool_set.reset_mock()
        pool = ceph.models.CephPool(id=0, name='test1', pg_num=0, type='replicated',
                                    tier_of=ceph.models.CephPool(id=999))
        pool.save()
        monApi_mock.return_value.osd_tier_add.assert_called_with(pool='test', tierpool='test1')

    @mock.patch('ceph.models.CephPool.objects')
    @mock.patch('ceph.models.rados')
    @mock.patch('ceph.models.MonApi', autospec=True)
    def test_call_order(self, monApi_mock, rados_mock, cephpool_objects_mock):
        """
        .. seealso: http://stackoverflow.com/questions/7242433/asserting-successive-calls-to-a-mock-method
        """
        cephpool_objects_mock.nodb_context = mock.Mock(fsid='hallo')
        cephpool_objects_mock.get.return_value = ceph.models.CephPool(id=0, name='test', pg_num=0, type='replicated')

        # Checking the order of different calls.
        pool = ceph.models.CephPool(name='test1', pg_num=0, type='replicated', cache_mode='writeback',
                                    tier_of=ceph.models.CephPool(id=1))
        pool.save()
        calls = [
            mock.call.osd_pool_create('test1', 0, 0, 'replicated', None),
            mock.call.osd_tier_add('test', 'test1'),
            mock.call.osd_tier_cache_mode('test1', 'writeback')
        ]
        monApi_mock.return_value.assert_has_calls(calls)

        # Checking the reverse order.
        # FIXME: as get() returns pool with id=0, save() cannot determine the original tier_of, resulting
        #        in wired parameters to osd_tier_remove.
        cephpool_objects_mock.get.return_value = ceph.models.CephPool(id=0, name='test', pg_num=0, type='replicated',
                                                                      cache_mode='writeback',
                                                                      tier_of=ceph.models.CephPool(id=0, name='test',
                                                                                                   pg_num=0,
                                                                                                   type='replicated'))
        monApi_mock.return_value.reset_mock()
        pool = ceph.models.CephPool(id=0, name='test', pg_num=0, type='replicated', cache_mode='none', tier_of=None)
        pool.save()
        calls = [
            mock.call.osd_tier_cache_mode('test', 'none'),
            mock.call.osd_tier_remove('test', 'test'),
        ]
        monApi_mock.return_value.assert_has_calls(calls)


class UndoFrameworkTest(TestCase):
    class Foo(object):
        def __init__(self):
            self.val = 0

        @undoable
        def add(self, x):
            self.val += x
            yield self.val
            self.val -= x

        @undoable
        def multi(self, x):
            self.val *= x
            yield self.val
            self.val /= x

        @undoable
        def minus(self, x):
            self.val -= x
            yield self.val
            self.add(x)

        @undoable
        def div(self):
            self.val /= 0
            yield self.val
            assert False

    def test_exception(self):
        foo = UndoFrameworkTest.Foo()
        foo.add(100)
        with undo_transaction(foo, NotImplementedError):
            self.assertEqual(foo.val, 100)
            foo.add(4)
            self.assertEqual(foo.val, 104)
            foo.add(2)
            self.assertEqual(foo.val, 106)
            raise NotImplementedError()
        self.assertEqual(foo.val, 100)

    def test_success(self):
        foo = UndoFrameworkTest.Foo()
        foo.add(100)
        self.assertEqual(foo.val, 100)
        with undo_transaction(foo, NotImplementedError):
            self.assertEqual(foo.val, 100)
            self.assertEqual(foo.add(4), 104)
            self.assertEqual(foo.val, 104)
            foo.add(2)
            self.assertEqual(foo.val, 106)
        self.assertEqual(foo.val, 106)

    def test_unknown_exception(self):
        foo = UndoFrameworkTest.Foo()
        try:
            with undo_transaction(foo, NotImplementedError):
                self.assertEqual(foo.val, 0)
                foo.add(4)
                self.assertEqual(foo.val, 4)
                raise ValueError()
        except ValueError:
            self.assertEqual(foo.val, 4)
            return
        self.fail('no exception')

    def test_broken_undo(self):
        foo = UndoFrameworkTest.Foo()
        try:
            with undo_transaction(foo, NotImplementedError):
                foo.add(4)
                self.assertEqual(foo.val, 4)
                foo.multi(0)
                self.assertEqual(foo.val, 0)
                raise NotImplementedError()
        except NotImplementedError:
            self.fail('wrong type')
        except ZeroDivisionError:
            return
        self.fail('no exception')

    def test_undoable_undo(self):
        with undo_transaction(UndoFrameworkTest.Foo(), NotImplementedError) as foo:
            self.assertEqual(foo.val, 0)
            foo.add(4)
            self.assertEqual(foo.val, 4)
            self.assertEqual(foo.minus(1), 3)
            self.assertEqual(foo.val, 3)
            raise NotImplementedError()
        self.assertEqual(foo.val, 0)

    def test_excption_in_func(self):
        foo = UndoFrameworkTest.Foo()
        foo.add(100)
        with undo_transaction(foo, ZeroDivisionError):
            foo.add(4)
            foo.div()
            self.fail('div by 0')
        self.assertEqual(foo.val, 100)

    def test_re_raise(self):
        try:
            with undo_transaction(UndoFrameworkTest.Foo(), ValueError, re_raise_exception=True):
                raise ValueError()
        except ValueError:
            return
        self.fail('no exception')


class LibradosTest(TestCase):
    @mock.patch.object(ceph.librados.Client, 'connect')
    @mock.patch('ceph.librados.MonApi', autospec=True)
    def test_osd_tree(self, monApi_mock, connect_mock):
        tree = [json.loads("""{
            "id": 12,
            "name": "osd.12",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.229996,
            "depth": 2,
            "exists": 1,
            "status": "up",
            "reweight": 1,
            "primary_affinity": 1
        }""")] * 3
        tree += [json.loads("""{
            "id": -10,
            "name": "z2-dfs06",
            "type": "host",
            "type_id": 1,
            "children": [12]
        }""")] * 3
        tree += [json.loads("""  {
        "id": -17,
            "name": "z1-dfs",
            "type": "zone",
            "type_id": 2,
            "children": [-10]
        }""")] * 2
        tree += [json.loads("""  {
            "id": -19,
            "name": "sata_raid_bucket",
            "type": "pool",
            "type_id": 3,
            "children": [-17]
        }""")] * 2
        monApi_mock.return_value.osd_tree.return_value = {'nodes': tree}
        res = ceph.librados.Client().list_osds()
        self.assertEqual(res, [
            {
                "id": 12,
                "name": "osd.12",
                "type": "osd",
                "type_id": 0,
                "crush_weight": 0.229996,
                "exists": 1,
                "status": "up",
                "reweight": 1,
                "primary_affinity": 1,
                "hostname": "z2-dfs06"
            }
        ])

    @mock.patch('ceph.models.rados', autospec=True)
    @mock.patch.object(ceph.models.librados.Client, 'connect')
    @mock.patch('ceph.models.MonApi', autospec=True)
    @mock.patch('ceph.models.librados.MonApi', autospec=True)
    def test_ceph_osd_list(self, librados_monApi_mock, monApi_mock, connect_mock, rados):
        rados.__getitem__ = mock.MagicMock(return_value=ceph.models.librados.Client())
        with open_testdata("tests/ceph-osd-dump.json") as f:
            osd_dump = json.load(f)
            monApi_mock.return_value.osd_dump.return_value = osd_dump
            librados_monApi_mock.return_value.osd_dump.return_value = osd_dump
        with open_testdata("tests/ceph-osd-tree.json") as f:
            osd_tree = json.load(f)
            monApi_mock.return_value.osd_tree.return_value = osd_tree
            librados_monApi_mock.return_value.osd_tree.return_value = osd_tree
        class Ctx:
            fsid = ''
        osds = ceph.models.CephOsd.get_all_objects(Ctx(), None)
        names = [osd.name for osd in osds]
        self.assertEqual(names, [u'osd.0', u'osd.1', u'osd.2', u'osd.4', u'osd.5', u'osd.6', u'osd.7', u'osd.8',
                                 u'osd.9', u'osd.11', u'osd.12', u'osd.13', u'osd.14', u'osd.15'])
