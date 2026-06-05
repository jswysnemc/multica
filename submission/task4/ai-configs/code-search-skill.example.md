# Code Search Workflow

## Purpose

Use semantic search to locate unfamiliar implementation paths before reading files manually.

## Steps

1. Ask one precise natural-language question naming the behavior to trace.
2. Use semantic search to identify likely files, functions, tests and SQL queries.
3. Read only the returned file ranges.
4. Confirm exact line references with numbered file output.
5. Use exact search only inside known files or known directories.
6. If the result is ambiguous, run a narrower semantic query.

## Example Query

```text
Where are daemon heartbeat, runtime offline detection, task claim concurrency and reconnect behavior implemented? Include handlers, service methods, SQL queries and tests.
```
