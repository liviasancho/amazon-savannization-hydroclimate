# Contributing

This repository supports the reproducible computational workflow of an associated scientific manuscript.

Repository maintenance is currently centralized by the repository owner.

## Contributions from manuscript coauthors

Coauthors may provide:

- scripts;
- notebooks;
- documentation;
- methodological descriptions;
- test data;
- metadata.

The repository maintainer will review, standardize, and integrate contributed materials.

## Contribution requirements

Contributed scripts should:

1. avoid hard-coded personal paths;
2. clearly document required inputs and generated outputs;
3. identify external datasets and software dependencies;
4. include comments sufficient to understand the analysis workflow;
5. avoid redistributing third-party datasets unless their licenses explicitly permit redistribution;
6. preserve reproducibility by documenting important parameters and versions.

## File naming

Use descriptive lowercase names with underscores.

Examples:

```text
calculate_spei.py
vegetation_change_analysis.py
fire_frequency_analysis.py
```

Avoid development suffixes in final files:

```text
script_v2.py
script_final.py
script_final2.py
```

Software versions are tracked through Git history and repository releases.
