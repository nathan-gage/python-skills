---
title: Make the Plugin Surface Explicit When Autoload Bites
impact: LOW-MEDIUM
impactDescription: uninvited plugins change suite behavior when unrelated dependencies bump
tags: structure, plugins, configuration
references: https://docs.pytest.org/en/stable/how-to/plugins.html#deactivating-unregistering-a-plugin-by-name, https://docs.pytest.org/en/stable/reference/reference.html#envvar-PYTEST_DISABLE_PLUGIN_AUTOLOAD
---

## Make the Plugin Surface Explicit When Autoload Bites

pytest autoloads every installed package that declares a `pytest11` entry point — including packages that arrived transitively, for the application's sake, that no test uses. That default is fine for most suites. It stops being fine when an uninvited plugin wraps test execution, adds retries or telemetry, or slows collection — and nothing in the repository records the plugin surface, so suite behavior silently shifts whenever an unrelated dependency bumps.

**Incorrect (observed drift, no decision recorded):**

```toml
# pyproject.toml — an app dependency ships a pytest plugin
[project]
dependencies = ["observability-sdk"]      # registers a pytest11 entry point

[tool.pytest.ini_options]
testpaths = ["tests"]
# collection got slower and runs now happen under the SDK's tracing wrapper —
# behavior nobody chose, invisible in config, different on machines without the SDK
```

**Correct (drift observed → surface made explicit):**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-p no:observability_sdk"       # decision recorded next to the config it affects
```

Diagnose with `pytest --trace-config` (lists every active plugin) or compare a run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` plus explicit `-p` flags for the plugins the suite actually uses — the allowlist form, which makes the whole surface declared rather than inherited. Symptoms that warrant the audit: collection noticeably slower than test time, retries or telemetry no config requested, tests behaving differently on one machine. Plugins the suite genuinely depends on belong in dev dependencies by name.

**Keep autoload when quiet:** leaving autoload alone in the absence of symptoms is a fine default, not a violation.
