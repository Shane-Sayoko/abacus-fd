"""Tests for generated ABACUS INPUT files."""

import os
import tempfile
import unittest

from abacus_fd.core import copy_input_without_output_parameters


class GeneratedInputTest(unittest.TestCase):
    def test_omits_case_insensitive_output_parameters_only_from_copy(self):
        source_contents = (
            "INPUT_PARAMETERS\n"
            "suffix          benzene\n"
            "cal_syns        1\n"
            "CAL_FORCE       1 # analytical forces\n"
            "cal_stress      0\n"
            "# cal_force 1\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "INPUT.source")
            target = os.path.join(directory, "INPUT")
            with open(source, "w") as handle:
                handle.write(source_contents)

            copy_input_without_output_parameters(source, target)

            with open(source, "r") as handle:
                self.assertEqual(handle.read(), source_contents)
            with open(target, "r") as handle:
                self.assertEqual(
                    handle.read(),
                    "INPUT_PARAMETERS\n"
                    "suffix          benzene\n"
                    "cal_stress      0\n"
                    "# cal_force 1\n",
                )


if __name__ == "__main__":
    unittest.main()
