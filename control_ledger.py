import json
import sys
from collections import defaultdict


VALID_SOURCES = {
    "POLICY",
    "HUMAN",
    "SCRIPTED",
    "SAFETY",
    "SHARED",
    "UNKNOWN",
}


def load_episode(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_episode(data):
    errors = []

    if "episode_id" not in data:
        errors.append("Missing episode_id.")

    if "segments" not in data or not isinstance(data["segments"], list):
        errors.append("Missing or invalid segments list.")
        return errors

    for index, segment in enumerate(data["segments"]):
        start = segment.get("start")
        end = segment.get("end")
        source = segment.get("source")

        if not isinstance(start, (int, float)):
            errors.append(f"Segment {index}: invalid start time.")

        if not isinstance(end, (int, float)):
            errors.append(f"Segment {index}: invalid end time.")

        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            if end <= start:
                errors.append(f"Segment {index}: end must be greater than start.")

        if source not in VALID_SOURCES:
            errors.append(
                f"Segment {index}: invalid source {source!r}."
            )

    return errors


def analyse_episode(data):
    totals = defaultdict(float)

    for segment in data["segments"]:
        duration = segment["end"] - segment["start"]
        totals[segment["source"]] += duration

    recorded_time = sum(totals.values())

    support_counts = defaultdict(int)

    for event in data.get("support_events", []):
        event_type = event.get("type", "UNKNOWN")
        support_counts[event_type] += 1

    return recorded_time, totals, support_counts


def print_report(data, recorded_time, totals, support_counts):
    print(f"Episode: {data['episode_id']}")
    print()
    print(f"Recorded control time: {recorded_time:.1f} s")
    print()

    for source in VALID_SOURCES:
        duration = totals.get(source, 0.0)

        if duration == 0:
            continue

        share = (
            duration / recorded_time * 100
            if recorded_time > 0
            else 0
        )

        print(f"{source:<10} {duration:>6.1f} s {share:>6.1f}%")

    print()
    print("Support events:")

    if support_counts:
        for event_type, count in support_counts.items():
            print(f"{event_type:<10} {count}")
    else:
        print("None")

    print()
    print("Success:")
    print("YES" if data.get("success") is True else "NO")

    print()
    print(
        "Shares describe control authority, not causal contribution."
    )


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {"validate", "analyse"}:
        print(
            "Usage: python control_ledger.py "
            "[validate|analyse] episode.json"
        )
        sys.exit(1)

    command = sys.argv[1]
    path = sys.argv[2]

    try:
        data = load_episode(path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error reading episode file: {error}")
        sys.exit(1)

    errors = validate_episode(data)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    if command == "validate":
        print("Validation passed.")
        return

    recorded_time, totals, support_counts = analyse_episode(data)

    print_report(
        data,
        recorded_time,
        totals,
        support_counts,
    )


if __name__ == "__main__":
    main()