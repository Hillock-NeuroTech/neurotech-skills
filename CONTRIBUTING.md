# Contributing

Hillock is only as good as the practice it encodes. Useful contributions:

- **Improve a skill**: a missing step, a better default, a newer tool,
  a correction. Cite the source.
- **Add a device, dataset or format** to the relevant skill.
- **Add or improve a script** in a skill's `scripts/`, with a test case
  that has a known answer.
- **Review a bundle** as a practitioner; reviewed skills carry your name.
- **Add a benchmark task** (below).

## Add a benchmark task

A good task has:

1. **An ordinary request.** Something you would really ask an assistant:
   extend a script, rerun with a change, write the results sentence. Do not
   name the trap.
2. **A hidden trap** you have seen cause a wrong answer in real work.
3. **A known truth.** Synthetic data built so the honest answer is exact
   (for example: no real signal, so honest accuracy is chance), or a
   calculation with one right value.
4. **A grader** that checks the answer by code, with a threshold between the
   naive and the careful result.
5. **A validation** in the set's `reference.py`: the naive path must fail the
   grader and a careful path must pass it.

Open a pull request with the generator function, the grader check and the
reference lines. Say where the trap comes from (paper, forum thread, your own
lab) so others can judge it.

## Report a result

Ran the benchmark on another model or with a skill loaded? Open an issue
with the model name and version, date, how it was run, and the `results.json`
the grader wrote. Failures are as welcome as passes.

## Review

Every task set lists a named reviewer once one has signed off. If you work
in the area and want to review a set, open an issue.
