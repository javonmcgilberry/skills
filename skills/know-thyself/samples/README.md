# Samples

| Pair | Shows | Provenance |
|---|---|---|
| `opener.before.txt` → `opener.after.txt` | A coach-mode rewrite of a plain opener | Synthetic; contains no corpus text. The rewrite adds Altitude (keep it fast), Depth (trace and profile, hard target, outside check), scope, and shipping authority, and skips Range because a load-time fix has one right answer. The 2-second target is illustrative. |

`convo.detect` on the text of `opener.after.txt` should find `altitude`, `raw_material`, `hard_target`, `outside_judge`, `aim_high`, `scope_control`, and `shipping_authority`, and none of the ambition signals on `opener.before.txt`. `../scripts/validate_skill.py` checks both.
