# Cold-read questions

Write these before the rewrite and do not change them after. Replace the bracketed parts with the repository's own nouns. Keep 10 to 12, and keep each one answerable from docs and checkable in code.

1. In one paragraph, how does [the core data] get from [its source] to [where users see it]? Name the processes and the main code entry points.
2. What is [the central concept a newcomer must grasp], and why is it not [the thing it is easily confused with]?
3. What does [the main user action] do, what does it preserve, and where is its code?
4. What happens at runtime, from [start] to [working result]? Name the files that start that path.
5. Who owns [the critical operation, such as submission, payment or write], including validation and what follows it?
6. Give the exact commands to run everything locally from a fresh clone, and the address of each process.
7. Where do the env values come from, which files hold them, and which keys are secrets that must never reach the client?
8. Where does [the trickiest mapping or transformation] live on each side, and how does it match things up?
9. How do you run [the main test suite], and what does it not cover?
10. What differs between [this repository and its sibling, or this and the previous version], and why? Name at least three concrete differences.
11. How is a new version released, and how do you roll one back?
12. [A realistic symptom] happens. Where do you look first, and in what order?
