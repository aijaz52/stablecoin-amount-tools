import contextlib
import io
import unittest

import stablecoin_amounts as sc


class ConversionTests(unittest.TestCase):
    def test_to_units_basic_and_canonical_zero(self):
        self.assertEqual(sc.to_units("12.3456", 6), "12345600")
        self.assertEqual(sc.to_units("00012.3400", 6), "12340000")
        self.assertEqual(sc.to_units("0", 6), "0")
        self.assertEqual(sc.to_units(".5", 2), "50")
        self.assertEqual(sc.to_units("1.", 2), "100")

    def test_to_units_exact_boundary(self):
        self.assertEqual(sc.to_units("1.234567", 6), "1234567")
        self.assertEqual(sc.to_units("1.234567000", 6), "1234567")
        self.assertEqual(sc.to_units("7", 0), "7")

    def test_to_units_rejects_nonzero_excess_precision(self):
        with self.assertRaisesRegex(ValueError, "more than 2"):
            sc.to_units("1.001", 2)
        with self.assertRaises(ValueError):
            sc.to_units(".00001", 4)

    def test_from_units_basic_and_small_values(self):
        self.assertEqual(sc.from_units("12345600", 6), "12.3456")
        self.assertEqual(sc.from_units("000050", 2), "0.5")
        self.assertEqual(sc.from_units("1", 6), "0.000001")
        self.assertEqual(sc.from_units("0", 6), "0")
        self.assertEqual(sc.from_units("7", 0), "7")

    def test_round_trip_without_float(self):
        for value, decimals in (("123.4500", 6), ("0.000001", 6), ("999", 0), (".42", 3)):
            expected = value.rstrip("0").rstrip(".") or "0"
            if expected.startswith("."):
                expected = "0" + expected
            self.assertEqual(sc.from_units(sc.to_units(value, decimals), decimals), expected)

    def test_rejects_negative_exponent_and_bad_syntax(self):
        for value in ("-1", "+1", "1e3", "1E-3", "nan", "", "1,000", " 1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    sc.to_units(value, 2)
        for value in ("-1", "+1", "1.0", "1e3", "", " 1"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    sc.from_units(value, 2)

    def test_rejects_bad_decimals_including_bool(self):
        for decimals in (-1, 256, True, False, 2.0, "2"):
            with self.subTest(decimals=decimals):
                with self.assertRaises(ValueError):
                    sc.to_units("1", decimals)
                with self.assertRaises(ValueError):
                    sc.from_units("1", decimals)

    def test_digit_limit(self):
        self.assertEqual(len(sc.to_units("9" * sc.MAX_DIGITS, 0)), sc.MAX_DIGITS)
        with self.assertRaisesRegex(ValueError, "safety limit"):
            sc.to_units("9" * (sc.MAX_DIGITS + 1), 0)
        with self.assertRaisesRegex(ValueError, "safety limit"):
            sc.from_units("9" * (sc.MAX_DIGITS + 1), 0)

    def test_rejects_unicode_numeral_lookalikes(self):
        for value in ("١", "０", "1.٢", "²"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    sc.to_units(value, 6)
                with self.assertRaises(ValueError):
                    sc.from_units(value, 6)

    def test_large_integer_round_trips(self):
        for decimals in (0, 6, 18, 255):
            units = "1234567890" * 100
            self.assertEqual(sc.to_units(sc.from_units(units, decimals), decimals), units)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = sc.main(list(args))
        return status, output.getvalue().strip()

    def test_cli_subcommands(self):
        self.assertEqual(self.run_cli("to-units", "1.25", "--decimals", "6"), (0, "1250000"))
        self.assertEqual(self.run_cli("from-units", "1250000", "--decimals", "6"), (0, "1.25"))

    def test_cli_requires_decimals(self):
        with self.assertRaises(SystemExit) as raised:
            sc.main(["to-units", "1"])
        self.assertEqual(raised.exception.code, 2)

    def test_cli_rejects_unicode_decimals(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                sc.main(["to-units", "1", "--decimals", "٦"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
