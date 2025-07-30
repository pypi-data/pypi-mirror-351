import unittest
from src.modules.utilities import parse_and_save_ipmi_output


class TestUtilities(unittest.TestCase):
    def test_parse_and_save_ipmi_output(self):
        sample_output = """
        Instantaneous power reading: 150 Watts
        Minimum during sampling period: 100 Watts
        Maximum during sampling period: 200 Watts
        Average power reading over sample period: 125 Watts
        Sampling period: 10 Seconds.
        Power reading state is: active
        """
        result = parse_and_save_ipmi_output(sample_output, "now", "2025-01-01")
        self.assertEqual(result["Instantaneous power reading"], "150 Watts")


if __name__ == "__main__":
    unittest.main()
