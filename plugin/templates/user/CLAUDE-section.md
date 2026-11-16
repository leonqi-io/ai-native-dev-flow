<!-- Paste into ~/.claude/CLAUDE.md. Applies to every project. -->

## Code conventions for agent-written code
- Names say what they hold. A long descriptive name is fine; an abbreviation the reader has to decode is not.
- Comment what is hard to follow, and the *why* behind a choice that is not obvious. Do not comment what the line already says.
- When code changes, the comments next to it change in the same commit.
- Short functions, shallow nesting, no duplicated logic. No spaghetti code: one function, one job.
