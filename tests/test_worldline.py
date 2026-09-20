import unittest

from worldline import spatial_coverage


class WorldlineTests(unittest.TestCase):
    def test_counts_labelled_and_missing_xyz(self):
        episode = {
            "episode_id": "ep-worldline",
            "segments": [
                {"start": 0.0, "end": 10.0, "source": "POLICY", "xyz": [0.2, 0.0, 0.8]},
                {"start": 10.0, "end": 15.0, "source": "HUMAN", "xyz": [0.4, 0.1, 0.7]},
                {"start": 15.0, "end": 20.0, "source": "POLICY"},
            ],
        }

        labelled, missing, total = spatial_coverage(episode)

        self.assertEqual(total, 3)
        self.assertEqual(labelled, 2)
        self.assertEqual(missing, 1)

    def test_missing_xyz_is_not_invented(self):
        episode = {
            "episode_id": "no-space",
            "segments": [
                {"start": 0.0, "end": 5.0, "source": "POLICY"},
            ],
        }

        labelled, missing, total = spatial_coverage(episode)

        self.assertEqual(total, 1)
        self.assertEqual(labelled, 0)
        self.assertEqual(missing, 1)