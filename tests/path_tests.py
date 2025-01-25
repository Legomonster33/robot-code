import unittest

from onshape_api.paths.paths import DocumentPath, ElementPath, InstancePath

inst_path = InstancePath("1", "2")
same_path = InstancePath("1", "2")

doc_path = DocumentPath("1")
element_path = ElementPath("1", "2", "5")


class TestPathMethods(unittest.TestCase):
    def test_basic_comparisons(self):
        self.assertTrue(inst_path == same_path)
        self.assertFalse(inst_path is same_path)

    def test_eq(self):
        self.assertTrue(inst_path.__eq__(same_path))

    def test_hash(self):
        self.assertTrue(inst_path.__hash__() == same_path.__hash__())

    def test_in(self):
        self.assertTrue(inst_path in [same_path])
        self.assertTrue(inst_path in {same_path})

    def test_conversions(self):
        self.assertFalse(inst_path == doc_path)
        self.assertFalse(inst_path == element_path)
        self.assertFalse(inst_path is element_path)
        self.assertFalse(doc_path is inst_path)

    def test_in_conversions(self):
        self.assertFalse(doc_path in [inst_path])
        self.assertFalse(doc_path in {inst_path})
        self.assertFalse(inst_path in [element_path])
        self.assertFalse(inst_path in {element_path})
