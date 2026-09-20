import json
import math
import sys


def is_xyz(value):
    if not isinstance(value, list) or len(value) != 3:
        return False
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            return False
        if not math.isfinite(item):
            return False
    return True


def spatial_coverage(episode):
    segments = episode.get("segments") or []
    labelled = 0
    missing = 0

    for segment in segments:
        if is_xyz(segment.get("xyz")):
            labelled += 1
        else:
            missing += 1

    return labelled, missing, len(segments)


def main():
    if len(sys.argv) != 2:
        print("Usage: python worldline.py <episode.json>")
        sys.exit(2)

    with open(sys.argv[1], encoding="utf-8") as handle:
        episode = json.load(handle)

    labelled, missing, total = spatial_coverage(episode)
    episode_id = episode.get("episode_id", "unknown")

    print(f"Episode: {episode_id}")
    print(f"Segments: {total}")
    print(f"Spatial labelled: {labelled}")
    print(f"Spatial missing: {missing}")
    print("Missing spatial data stays missing. It is not inferred.")


if __name__ == "__main__":
    main()