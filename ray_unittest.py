import unittest
import vector


class TestVectorMethods(unittest.TestCase):

    def test_vectoraddition(self):
        a = vector.Vec3(1, 2, 3)
        b = vector.Vec3(4, 8, 10)
        self.assertEqual((a + b).x, 5.0)
        self.assertEqual((a + b).y, 10.0)
        self.assertEqual((a + b).z, 13.0)

    def test_vectordivision(self):
        a = vector.Vec3(2, 4, 8) / 2
        self.assertEqual(a.x, 1.0)
        self.assertEqual(a.y, 2.0)
        self.assertEqual(a.z, 4.0)


if __name__ == '__main__':
    unittest.main()
