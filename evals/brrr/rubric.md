# Brrr evaluation rubric

The routing eval gives Brrr a request and a complete evidence packet, then asks for the next action. It measures whether the skill chooses the right workflow boundary before any implementation begins.

Each response receives up to 100 points:

- 50 points for choosing the expected route.
- 20 points for avoiding a route that contradicts the evidence.
- 20 points for using enough case-specific evidence to ground the route.
- 10 points for keeping the next-action response under 140 words.

The routes are direct execution, Lock In, heavier execution, and execution without publication. This eval does not score code quality. The end-to-end forward test covers the implementation loop, progress record, tests, and publication boundary.
