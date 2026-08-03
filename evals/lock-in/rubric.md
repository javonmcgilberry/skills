# Lock In evaluation rubric

Each response is the first user-facing message produced from the request and evidence packet. The evaluator scores whether Lock In pauses at the right point instead of completing the brief on its own.

The deterministic score is out of 100:

- 30 points when the response asks for a user decision or confirmation.
- 15 points when it asks exactly one question.
- 20 points when it gives a recommendation.
- 20 points when it does not produce the final implementation brief before the checkpoint.
- 15 points when it mentions enough case-specific evidence to make the question useful.

A response loses 20 points when it asks for a fact already supplied by the evidence packet. Scores cannot fall below zero.

The current skill should improve the clear and evidence-resolvable cases without becoming more verbose than the pre-checkpoint version. Ambiguous cases should still ask about the decision that changes the contract most.
