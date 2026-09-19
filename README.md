# control-ledger

A small reporting tool for recording control authority and support events in robot rollouts.

`control-ledger` reads simple episode logs and reports who or what had control during a robot rollout, alongside external support events such as resets and setup.

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

V0.1 supports:

- `POLICY`
- `HUMAN`
- `SCRIPTED`
- `SAFETY`
- `SHARED`
- `UNKNOWN`

Unknown time is reported as `UNKNOWN`.

It is never silently counted as `POLICY`.

## Example

Input:

```json
{
  "episode_id": "ep-017",
  "success": true,
  "segments": [
    {
      "start": 0.0,
      "end": 10.0,
      "source": "POLICY"
    },
    {
      "start": 10.0,
      "end": 15.0,
      "source": "HUMAN"
    },
    {
      "start": 15.0,
      "end": 20.0,
      "source": "POLICY"
    }
  ],
  "support_events": [
    {
      "type": "RESET"
    }
  ]
}
```

Example output:

```text
Episode: ep-017

Recorded control time: 20.0 s

POLICY      15.0 s   75.0%
HUMAN        5.0 s   25.0%

Support events:
RESET      1

Success:
YES

Shares describe control authority, not causal contribution.
```

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
- missing segment lists

Gaps between recorded segments are reported as `UNKNOWN`.

They are not silently assigned to `POLICY`.

## Design principles

### Report, don't score

V0.1 does not produce:

- an autonomy score
- a capability score
- a residual-debt score
- labels such as "highly autonomous"

The tool reports recorded facts.

### Control and support are separate

Time inside the rollout describes control authority.

External events such as resets and setup are reported separately and are not forced into the control-time denominator.

### Unknown stays unknown

Missing or ambiguous control authority is reported as `UNKNOWN`.

The tool does not infer model control from missing data.

## Scope

V0.1 is intentionally small.

It can:

- validate episode logs
- analyse control segments
- calculate recorded control-time shares
- report support events
- report unknown gaps
- reject invalid control data
- output a human-readable report

It does not attempt to determine consciousness, agency, responsibility, autonomy, or causal contribution.

## Status

Early prototype.

The current examples are synthetic and are intended to test the reporting format before the tool is applied to real robot rollout logs.

## License

MIT