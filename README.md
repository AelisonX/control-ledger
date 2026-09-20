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

## Optional position labels

A segment may include optional `xyz`.

`xyz` counts as labelled only if it is three finite numbers.

Missing `xyz`, the wrong shape, or a fake value such as a place name is counted as missing.

The tool does not infer a position.

A log can name the driver and still omit the room.

Example:

```json
{
  "episode_id": "ep-worldline",
  "duration": 20.0,
  "success": true,
  "segments": [
    {
      "start": 0.0,
      "end": 10.0,
      "source": "POLICY",
      "xyz": [0.2, 0.0, 0.8]
    },
    {
      "start": 10.0,
      "end": 20.0,
      "source": "POLICY"
    }
  ],
  "support_events": []
}