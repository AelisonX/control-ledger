import unittest

from control_ledger import (
    analyse_episode,
    fill_unknown_gaps,
    validate_episode,
)


class ControlLedgerTests(unittest.TestCase):
    def test_valid_episode_passes(self):
        data = {
            "episode_id": "valid",
            "success": True,
            "segments": [
                {"start": 0.0, "end": 5.0, "source": "POLICY"},
                {"start": 5.0, "end": 10.0, "source": "HUMAN"},
            ],
            "support_events": [],
        }

        self.assertEqual(validate_episode(data), [])

    def test_overlap_is_rejected(self):
        data = {
            "episode_id": "overlap",
            "segments": [
                {"start": 0.0, "end": 10.0, "source": "POLICY"},
                {"start": 8.0, "end": 15.0, "source": "HUMAN"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("Overlapping segments detected" in error for error in errors)
        )

    def test_invalid_source_is_rejected(self):
        data = {
            "episode_id": "invalid-source",
            "segments": [
                {"start": 0.0, "end": 5.0, "source": "ROBOT"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("invalid source" in error for error in errors)
        )

    def test_invalid_time_order_is_rejected(self):
        data = {
            "episode_id": "invalid-time",
            "segments": [
                {"start": 10.0, "end": 5.0, "source": "POLICY"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("end must be greater than start" in error for error in errors)
        )

    def test_missing_segments_is_rejected(self):
        data = {
            "episode_id": "missing-segments",
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("Missing or invalid segments list" in error for error in errors)
        )

    def test_gap_becomes_unknown(self):
        segments = [
            {"start": 0.0, "end": 5.0, "source": "POLICY"},
            {"start": 7.0, "end": 10.0, "source": "HUMAN"},
        ]

        completed = fill_unknown_gaps(segments)

        self.assertEqual(
            completed,
            [
                {"start": 0.0, "end": 5.0, "source": "POLICY"},
                {"start": 5.0, "end": 7.0, "source": "UNKNOWN"},
                {"start": 7.0, "end": 10.0, "source": "HUMAN"},
            ],
        )

    def test_analysis_counts_unknown_time(self):
        data = {
            "episode_id": "analysis-gap",
            "success": True,
            "segments": [
                {"start": 0.0, "end": 5.0, "source": "POLICY"},
                {"start": 7.0, "end": 10.0, "source": "HUMAN"},
            ],
            "support_events": [],
        }

        recorded_time, totals, support_counts, completed = analyse_episode(data)

        self.assertEqual(recorded_time, 10.0)
        self.assertEqual(totals["POLICY"], 5.0)
        self.assertEqual(totals["UNKNOWN"], 2.0)
        self.assertEqual(totals["HUMAN"], 3.0)
        self.assertEqual(dict(support_counts), {})
        self.assertEqual(len(completed), 3)


if __name__ == "__main__":
    unittest.main()