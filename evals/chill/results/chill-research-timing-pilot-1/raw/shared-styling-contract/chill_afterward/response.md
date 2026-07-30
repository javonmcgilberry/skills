Create one shared contract for style data, with a required core and optional visual extras. Keep each consumer’s rendering details and old field names outside the contract.

1. **Set the contract boundary.** Require `spacing`, `typography`, `foregroundColor`, `backgroundColor`, and `disabledState` because every consumer uses them [BASE]. Make `border?` and `shadow?` optional because only some consumers support them [OPTIONAL]. Include style values only, with no component layout, markup, or rendering logic [STRUCTURE].

2. **Create an adapter for each consumer.** Each adapter translates the shared fields into that consumer’s existing local shape. Old aliases stay in the adapters, so consumers can migrate independently without adding legacy names to the shared contract [COMPATIBILITY].

3. **Migrate one representative consumer first.** Pick one that uses every required field and preferably a border or shadow. Send its styles through the adapter without changing how it renders [ROLLOUT] [STRUCTURE].

4. **Validate that migration.** Check that spacing, typography, foreground and background colors, and disabled states still look and behave the same [BASE]. Confirm that missing borders or shadows produce no errors or unwanted output, while supported values render correctly [OPTIONAL]. Make sure legacy names exist only in the adapter [COMPATIBILITY].

5. **Migrate the remaining consumers.** Once those checks pass, add one adapter per consumer and move them over incrementally [ROLLOUT]. A migration is complete when required styles remain visually equivalent, optional styles work correctly, and the shared contract contains neither legacy aliases nor rendering details [BASE] [OPTIONAL] [STRUCTURE] [COMPATIBILITY].