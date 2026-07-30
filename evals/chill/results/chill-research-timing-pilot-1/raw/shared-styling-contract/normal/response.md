Define one shared style-data contract with required core fields and optional decoration fields. Keep consumer-specific rendering and legacy naming outside it.

1. **Define the contract boundary.** Require `spacing`, `typography`, `foregroundColor`, `backgroundColor`, and `disabledState`, since every consumer needs them [BASE]. Add `border?` and `shadow?` as optional fields because support varies by consumer [OPTIONAL]. The contract should contain values only, with no component hierarchy, markup, or rendering logic [STRUCTURE].

2. **Add explicit consumer adapters.** Each adapter converts the shared contract into its consumer’s local shape. Keep existing aliases inside these adapters rather than adding them to the shared types, so the contract stays consistent while consumers migrate independently [COMPATIBILITY].

3. **Migrate one representative consumer.** Choose a consumer that exercises all required fields and, if possible, at least one optional field. Route its styling through the adapter without changing its rendering behavior [ROLLOUT] [STRUCTURE].

4. **Validate the first migration.** Confirm that spacing, typography, foreground and background colors, and disabled styling match existing behavior [BASE]. Verify that omitted borders and shadows cause no errors or unintended output, while supported values render correctly [OPTIONAL]. Also confirm that legacy field names appear only in the adapter [COMPATIBILITY].

5. **Migrate the remaining consumers.** After focused validation passes, add one adapter per remaining consumer and move them onto the contract incrementally [ROLLOUT]. A consumer is complete when required styles remain visually equivalent, optional styles behave correctly, and no legacy aliases or rendering concerns have entered the shared contract [BASE] [OPTIONAL] [STRUCTURE] [COMPATIBILITY].