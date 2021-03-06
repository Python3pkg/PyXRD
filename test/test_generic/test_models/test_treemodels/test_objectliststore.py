#!/usr/bin/python

# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

import gobject
import unittest

from pyxrd.generic.models import DataModel
from mvc.adapters.gtk_support.treemodels import ObjectListStore
from mvc import PropIntel

__all__ = [
    'TestObjectListStore',
]


class _DummyObject(DataModel):
    class Meta(DataModel.Meta):
        properties = [
            PropIntel(name="name", data_type=str, is_column=True),
            PropIntel(name="number", data_type=float, is_column=True),
            PropIntel(name="test", data_type=object, is_column=True),
        ]

    name = ""
    number = 0
    test = object()

    pass # end of class

class _DummyParent(DataModel):
    class Meta(DataModel.Meta):

        properties = [
            PropIntel(name="attrib", data_type=object, class_type=_DummyObject),
        ]

    attrib = []

    pass # end of class


class TestObjectListStore(unittest.TestCase):

    def setUp(self):
        self.model = _DummyParent()
        prop = self.model.Meta.get_prop_intel_by_name("attrib")
        self.store = ObjectListStore(self.model, prop)

    def tearDown(self):
        super(TestObjectListStore, self).tearDown()
        del self.model

    def test_columns(self):
        self.assertEqual(self.store.get_n_columns(), len(_DummyObject.Meta.get_column_properties()))
        self.assertEqual(self.store.get_column_type(self.store.c_name), gobject.type_from_name("gchararray"))
        self.assertEqual(self.store.get_column_type(self.store.c_number), gobject.type_from_name("gdouble"))
        self.assertEqual(self.store.get_column_type(self.store.c_test), gobject.type_from_name("PyObject"))

    def test_convert(self):
        self.assertEqual(self.store.convert(1, "0.5"), 0.5)

    # TODO:
    # - test JSON serialisation
    # - test raw data

    pass # end of class
