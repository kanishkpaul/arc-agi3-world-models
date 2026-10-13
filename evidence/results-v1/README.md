# Historical result summaries

[← Research record](../../docs/README.md)

Published October 13, 2026. This bundle contains sanitized outcome measurements; no new solver run was performed for the update.

| File | Contents |
| :--- | :--- |
| [records.json](records.json) | Aggregate measurements, dates, protocols, and provenance labels |
| [tcca-per-game.csv](tcca-per-game.csv) | Twenty-five historical offline benchmark outcomes |
| [npass-per-game.csv](npass-per-game.csv) | Twenty-five discovery/replay outcome rows |
| [manifest.json](manifest.json) | File checksums, schema version, and disclosure scope |

The per-game tables include scores, completion, and aggregate interaction measurements. They exclude raw action sequences, model outputs, solver parameters, scorecard credentials, and source-machine paths.

```bash
python scripts/verify_results.py
```

Run that command from the repository root to check table arithmetic and artifact hashes. The script verifies internal consistency; it does not authenticate the original records or reconstruct the private solver.

The source records are preserved privately. Their labels in `records.json` identify the historical measurement being summarized, not publicly available raw downloads. See the [evaluation guide](../../docs/evaluation.md) for each evidence level.
