---
title: Fix encoding of booleans and datetimes inside lists
semver_level: patch
github_issues_resolved:
- https://github.com/stripe/stripe-python/issues/1956
---

Fix form and query encoding of `bool` and `datetime` values that are direct elements of a list or tuple. Those values were sent as Python `True`/`False` or a datetime string instead of `true`/`false` and a unix timestamp. This affects requests that pass lists of booleans or datetimes, including multipart uploads.
