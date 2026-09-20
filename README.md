# control-ledger

A small reporting tool for recording control authority and support events in robot rollouts.

`control-ledger` reads simple episode logs and reports who or what was recorded as holding control during a robot rollout, alongside external support events such as resets and setup.

It does not calculate an autonomy score.

It reports what was recorded.

## Why

A successful robot task can involve several different sources of control:

- model policy
- direct human control
- scripted behaviour
- safety systems
- shared control
- unknown control

It may also depend on support outside the control timeline, such as resets, setup, or manual recovery.

`control-ledger` keeps those categories separate instead of collapsing them into a single autonomy number.

## Control sources

The current format supports:

- `POLICY`
- `HUMAN`
- `SCRIPTED`
- `SAFETY`
- `SHARED`
- `UNKNOWN`

Unknown time is reported as `UNKNOWN`.

It is never silently counted as `POLICY`.

## Control authority

In this project, control authority means:

> the source recorded as selecting the command sent to the actuators during that interval.

This is narrower than autonomy, capability, responsibility, or causal contribution.

For example, `75% POLICY` means that the policy was recorded as holding command authority for 75% of the analysed timeline.

It does not mean that the policy caused 75% of the task success.

## Episode duration

An episode may optionally include a total `duration`.

Example:

```json
{
  "episode_id": "ep-017",
  "duration": 60.0,
  "success": true,
  "segments": [
    {
      "start": 0.0,
      "end": 20.0,
      "source": "POLICY"
    }
  ],
  "support_events": []
}
```

Because the episode lasts 60 seconds but only the first 20 seconds are labelled, the remaining 40 seconds are reported as `UNKNOWN`.

Example output:

```text
Episode: ep-017

Recorded control time: 60.0 s

POLICY       20.0 s   33.3%
UNKNOWN      40.0 s   66.7%

Support events:
None

Success:
YES

Shares describe control authority, not causal contribution.
```

If `duration` is omitted, the tool can only analyse the time covered by the supplied timeline.

## Usage

Validate an episode log:

```bash
python control_ledger.py validate examples/ep-017.json
```

Analyse an episode log:

```bash
python control_ledger.py analyse examples/ep-017.json
```

## Validation behaviour

The tool rejects:

- overlapping control segments
- invalid control sources
- end times that are not greater than start times
- negative start times
- invalid numeric values such as `NaN`
- boolean values used as timestamps
- non-object segment entries
- empty segment lists
- segments that extend beyond the declared episode duration

Small floating-point differences are tolerated so that harmless numerical noise does not create fake gaps or overlaps.

## Unknown stays unknown

Gaps between recorded segments are reported as `UNKNOWN`.

If an episode duration is provided, unrecorded time after the final segment is also reported as `UNKNOWN`.

The tool does not infer model control from missing data.

`UNKNOWN` should not be treated as a failure state or as a measure of robot quality.

A complete log and a capable robot are different things.

Coverage is not quality.

## Design principles

### Report, don't score

The tool does not produce:

- an autonomy score
- a capability score
- a responsibility score
- a residual-debt score
- labels such as "highly autonomous"

It reports recorded facts.

### Control and support are separate

Time inside the rollout describes control authority.

External events such as resets and setup are reported separately and are not forced into the control-time denominator.

### Unknown is not evidence

Missing control attribution is not silently reassigned to another source.

Unknown coverage should remain visible until better evidence is available.

### Shares are not causation

Control shares describe recorded command authority.

They do not describe causal contribution, capability, responsibility, or the support around the run.

## Scope

This project is intentionally small.

It can:

- validate episode logs
- analyse control segments
- calculate recorded control-time shares
- report support events
- report leading, internal, and trailing unknown gaps
- reject malformed or inconsistent control data
- output a human-readable report

It does not attempt to determine:

- consciousness
- agency
- personhood
- responsibility
- autonomy
- causal contribution

## Status

Early prototype.

The current examples are synthetic and are intended to test the reporting format before the tool is applied to real robot rollout logs.

## License

MIT