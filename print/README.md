# print/

Dated copies of the poster PDF that were actually sent to a printer or
carried to the venue, e.g. `poster_2026-11-01.pdf`. Produce one with

```bash
make print
```

Everything else named `*.pdf` in this repository is ignored by git; this
directory is the only exception, so that the exact file that was printed
stays reproducible from history.
