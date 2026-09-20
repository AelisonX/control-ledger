import json
import math
import sys
from collections import defaultdict


SOURCE_ORDER = [
    "POLICY",
    "HUMAN",
    "SCRIPTED",
    "SAFETY",
    "SHARED",
    "UNKNOWN",
]

VALID_SOURCES = set(SOURCE_ORDER)

TIME_EPSILON = 1e-6


def load_episode(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def is_valid_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_episode(data):
    errors = []

    if not isinstance(data, dict):
        return ["Episode must be a JSON object."]

    if "episode_id" not in data:
        errors.append("Missing episode_id.")

    segments = data.get("segments")

    if not isinstance(segments, list):
        errors.append("Missing or invalid segments list.")
        return errors

    if len(segments) == 0:
        errors.append("Segments list must not be empty.")
        return errors

    duration = data.get("duration")

    if duration is not None:
        if not is_valid_number(duration):
            errors.append("Invalid episode duration.")
        elif duration <= 0:
            errors.append("Episode duration must be greater than zero.")

    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            errors.append(f"Segment {index}: must be an object.")
            continue

        start = segment.get("start")
        end = segment.get("end")
        source = segment.get("source")

        if not is_valid_number(start):
            errors.append(f"Segment {index}: invalid start time.")

        if not is_valid_number(end):
            errors.append(f"Segment {index}: invalid end time.")

        if is_valid_number(start) and start < 0:
            errors.append(
                f"Segment {index}: start time must not be negative."
            )

        if is_valid_number(start) and is_valid_number(end):
            if end - start <= TIME_EPSILON:
                errors.append(
                    f"Segment {index}: end must be greater than start."
                )

        if source not in VALID_SOURCES:
            errors.append(
                f"Segment {index}: invalid source {source!r}."
            )

        if (
            duration is not None
            and is_valid_number(duration)
            and is_valid_number(end)
            and end - duration > TIME_EPSILON
        ):
            errors.append(
                f"Segment {index}: end exceeds episode duration."
            )

    if errors:
        return errors

    sorted_segments = sorted(
        segments,
        key=lambda segment: segment["start"],
    )

    for index in range(1, len(sorted_segments)):
        previous = sorted_segments[index - 1]
        current = sorted_segments[index]

        if current["start"] < previous["end"] - TIME_EPSILON:
            errors.append(
                "Overlapping segments detected: "
                f"{previous['start']}-{previous['end']} "
                f"and {current['start']}-{current['end']}."
            )

    return errors


def fill_unknown_gaps(segments, duration=None):
    sorted_segments = sorted(
        segments,
        key=lambda segment: segment["start"],
    )

    completed = []

    first = sorted_segments[0]

    if first["start"] > TIME_EPSILON:
        completed.append(
            {
                "start": 0.0,
                "end": first["start"],
                "source": "UNKNOWN",
            }
        )

    completed.append(first)

    for current in sorted_segments[1:]:
        previous = completed[-1]

        gap = current["start"] - previous["end"]

        if gap > TIME_EPSILON:
            completed.append(
                {
                    "start": previous["end"],
                    "end": current["start"],
                    "source": "UNKNOWN",
                }
            )

        completed.append(current)

    if duration is not None:
        last_end = completed[-1]["end"]
        trailing_gap = duration - last_end

        if trailing_gap > TIME_EPSILON:
            completed.append(
                {
                    "start": last_end,
                    "end": duration,
                    "source": "UNKNOWN",
                }
            )

    return completed


def analyse_episode(data):
    completed_segments = fill_unknown_gaps(
        data["segments"],
        data.get("duration"),
    )

    totals = defaultdict(float)

    for segment in completed_segments:
        duration = segment["end"] - segment["start"]
        totals[segment["source"]] += duration

    recorded_time = sum(totals.values())

    support_counts = defaultdict(int)

    for event in data.get("support_events", []):
        if isinstance(event, dict):
            event_type = event.get("type", "UNKNOWN")
        else:
            event_type = "UNKNOWN"

        support_counts[event_type] += 1

    return recorded_time, totals, support_counts, completed_segments


def print_report(data, recorded_time, totals, support_counts):
    print(f"Episode: {data['episode_id']}")
    print()
    print(f"Recorded control time: {recorded_time:.1f} s")
    print()

    for source in SOURCE_ORDER:
        duration = totals.get(source, 0.0)

        if duration <= TIME_EPSILON:
            continue

        share = (
            duration / recorded_time * 100
            if recorded_time > 0
            else 0
        )

        print(
            f"{source:<10} "
            f"{duration:>6.1f} s "
            f"{share:>6.1f}%"
        )

    print()
    print("Support events:")

    if support_counts:
        for event_type in sorted(support_counts):
            print(f"{event_type:<10} {support_counts[event_type]}")
    else:
        print("None")

    print()
    print("Success:")

    if data.get("success") is True:
        print("YES")
    elif data.get("success") is False:
        print("NO")
    else:
        print("UNKNOWN")

    print()
    print(
        "Shares describe control authority, not causal contribution."
    )


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {
        "validate",
        "analyse",
    }:
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

    recorded_time, totals, support_counts, _ = analyse_episode(data)

    print_report(
        data,
        recorded_time,
        totals,
        support_counts,
    )


if __name__ == "__main__":
    main()