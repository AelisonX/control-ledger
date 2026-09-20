import math
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

    def test_empty_segments_is_rejected(self):
        data = {
            "episode_id": "empty-segments",
            "segments": [],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("must not be empty" in error for error in errors)
        )

    def test_non_object_segment_is_rejected(self):
        data = {
            "episode_id": "bad-segment",
            "segments": [1],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("must be an object" in error for error in errors)
        )

    def test_boolean_time_is_rejected(self):
        data = {
            "episode_id": "bool-time",
            "segments": [
                {"start": True, "end": 5.0, "source": "POLICY"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("invalid start time" in error for error in errors)
        )

    def test_nan_time_is_rejected(self):
        data = {
            "episode_id": "nan-time",
            "segments": [
                {"start": 0.0, "end": math.nan, "source": "POLICY"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("invalid end time" in error for error in errors)
        )

    def test_negative_start_is_rejected(self):
        data = {
            "episode_id": "negative-start",
            "segments": [
                {"start": -1.0, "end": 5.0, "source": "POLICY"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("must not be negative" in error for error in errors)
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

    def test_trailing_gap_becomes_unknown(self):
        segments = [
            {"start": 0.0, "end": 20.0, "source": "POLICY"},
        ]

        completed = fill_unknown_gaps(
            segments,
            duration=60.0,
        )

        self.assertEqual(
            completed,
            [
                {"start": 0.0, "end": 20.0, "source": "POLICY"},
                {"start": 20.0, "end": 60.0, "source": "UNKNOWN"},
            ],
        )

    def test_analysis_counts_trailing_unknown_time(self):
        data = {
            "episode_id": "trailing-gap",
            "duration": 60.0,
            "success": True,
            "segments": [
                {"start": 0.0, "end": 20.0, "source": "POLICY"},
            ],
            "support_events": [],
        }

        recorded_time, totals, support_counts, completed = analyse_episode(data)

        self.assertEqual(recorded_time, 60.0)
        self.assertEqual(totals["POLICY"], 20.0)
        self.assertEqual(totals["UNKNOWN"], 40.0)
        self.assertEqual(dict(support_counts), {})
        self.assertEqual(len(completed), 2)

    def test_segment_cannot_exceed_episode_duration(self):
        data = {
            "episode_id": "too-long",
            "duration": 10.0,
            "segments": [
                {"start": 0.0, "end": 12.0, "source": "POLICY"},
            ],
        }

        errors = validate_episode(data)

        self.assertTrue(
            any("exceeds episode duration" in error for error in errors)
        )

    def test_small_float_noise_does_not_create_gap(self):
        segments = [
            {"start": 0.0, "end": 0.30000000000000004, "source": "POLICY"},
            {"start": 0.3, "end": 1.0, "source": "HUMAN"},
        ]

        completed = fill_unknown_gaps(segments)

        self.assertEqual(len(completed), 2)

    def test_small_float_noise_does_not_trigger_overlap(self):
        data = {
            "episode_id": "float-noise",
            "segments": [
                {
                    "start": 0.0,
                    "end": 0.30000000000000004,
                    "source": "POLICY",
                },
                {
                    "start": 0.3,
                    "end": 1.0,
                    "source": "HUMAN",
                },
            ],
        }

        self.assertEqual(validate_episode(data), [])


if __name__ == "__main__":
    unittest.main()