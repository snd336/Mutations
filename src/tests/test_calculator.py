from unittest import TestCase

from src.calculator import *


class CalculatorTest(TestCase):

    def test_aod(self):
        self.assertEqual(aod(2), -2)

    def test_aor(self):
        self.assertEqual(aor(2, 2), 8)

    def test_asr(self):
        self.assertEqual(asr(2, 2), 4)

    def test_bcr(self):
        self.assertEqual(bcr(), 'h')

    def test_cod(self):
        self.assertEqual(cod(True), True)

    def test_coi(self):
        self.assertEqual(coi(True), False)

    def test_crp(self):
        self.assertEqual(crp(), (1, 'test'))

    def test_DDL(self):
        temp_ddl = DDL()
        self.assertEqual(temp_ddl.ddl(), None)

    # TODO create tests with pass
    def test_EHD(self):
        pass

    def test_EXS(self):
        pass

    def test_IHD(self):
        temp_ihd = IHD()
        self.assertEqual(temp_ihd.y, 2)

    def test_IOD(self):
        temp_iod = IOD()
        self.assertEqual(temp_iod.foo(), None)

    def test_IOP(self):
        temp_iop = IOP()
        self.assertEqual(temp_iop.foo(), None)

    def test_lcr(self):
        self.assertEqual(lcr(2, 3), 2)

    def test_lod(self):
        self.assertEqual(lod(2), ~2)

    def test_lor(self):
        self.assertEqual(lor(2, 3), None)

    def test_ror(self):
        self.assertEqual(ror(2, 3), None)

    def test_SCD(self):
        temp_scd = SCD()
        self.assertEqual(temp_scd.foo(), None)

    def test_SCI(self):
        temp_sci = SCI()
        self.assertEqual(temp_sci.foo(), None)

    def test_sir(self):
        self.assertEqual(sir(2, [3]), None)

