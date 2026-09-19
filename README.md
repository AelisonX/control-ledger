# control-ledger

A small reporting tool for recording control authority and support events in robot rollouts.

`control-ledger` turns simple episode logs into transparent reports showing who or what had control during a robot rollout, alongside external support events such as resets and setup.

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