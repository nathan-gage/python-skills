# Python Best Practices

**Version 1.0.0**
Python Pytest
August 2026

> **Note:**
> This document is optimized for AI agents and LLMs that maintain, generate,
> or refactor Python codebases. Humans may also find it useful, but the
> guidance, examples, and framing prioritize consistency and pattern-matching
> for AI-assisted workflows.

---

## Abstract

Pytest discipline for agent consumption. 15 rules across 5 categories covering what deserves to be a committed test, deterministic concurrency testing, fixture isolation, mocking boundaries, and suite structure. Each rule is observational — it describes the pattern and what it costs, shows incorrect and correct code, and cites pytest or stdlib documentation where behavior is version- or configuration-dependent. The organizing principle: every committed test defends a named observable contract, and everything else — fixtures, mocks, parametrization, configuration — exists to keep that defense honest.

---

## Table of Contents

1. [Test Value](#1-test-value) — **HIGH**
   - 1.1 [Commit Tests That Protect Observable Contracts](#11-commit-tests-that-protect-observable-contracts)
   - 1.2 [Derive Expected Values Independently of the Implementation](#12-derive-expected-values-independently-of-the-implementation)
   - 1.3 [One Cohesive Behavior Per Test](#13-one-cohesive-behavior-per-test)
2. [Determinism](#2-determinism) — **HIGH**
   - 2.1 [Fix Nondeterminism, Don't Mask It](#21-fix-nondeterminism-dont-mask-it)
   - 2.2 [Synchronize on Events, Not Sleeps](#22-synchronize-on-events-not-sleeps)
   - 2.3 [Use Strict xfail So Unexpected Passes Fail](#23-use-strict-xfail-so-unexpected-passes-fail)
3. [Fixtures & Isolation](#3-fixtures-isolation) — **MEDIUM-HIGH**
   - 3.1 [Build Fixture Objects Through Production Constructors](#31-build-fixture-objects-through-production-constructors)
   - 3.2 [Give Fixtures the Narrowest Safe Scope](#32-give-fixtures-the-narrowest-safe-scope)
   - 3.3 [Restore Every Mutated Global, Including Absent Ones](#33-restore-every-mutated-global-including-absent-ones)
4. [Mocking](#4-mocking) — **MEDIUM-HIGH**
   - 4.1 [Assert the Wire Representation, Not the Python Intent](#41-assert-the-wire-representation-not-the-python-intent)
   - 4.2 [Mock at Stable IO Boundaries, Not the Behavior Under Test](#42-mock-at-stable-io-boundaries-not-the-behavior-under-test)
   - 4.3 [Patch Where the Name Is Looked Up, Not Where It's Defined](#43-patch-where-the-name-is-looked-up-not-where-its-defined)
5. [Structure & Execution](#5-structure-execution) — **MEDIUM**
   - 5.1 [Keep Test Module Import Identities Collision-Free](#51-keep-test-module-import-identities-collision-free)
   - 5.2 [Make the Plugin Surface Explicit When Autoload Bites](#52-make-the-plugin-surface-explicit-when-autoload-bites)
   - 5.3 [Parametrize Contract-Distinct Partitions](#53-parametrize-contract-distinct-partitions)

---

## 1. Test Value

**Impact: HIGH**

What deserves to be a committed test. Observable contracts over execution probes, independent oracles over implementation echoes. A test that can't fail for a real reason is weight, not coverage.

### 1.1 Commit Tests That Protect Observable Contracts

**Impact: HIGH (probe tests add runtime and maintenance cost while defending nothing)**

A committed test must protect a named, observable behavior with an assertion that fails for a plausible regression. Tests that merely *execute* code — call a function, assert the result "is not None", check no exception was raised — are development probes: useful while writing the code, weight once committed. They pass under almost any regression, so they defend nothing, while still costing runtime, maintenance, and reviewer attention.

**Incorrect (executes code; asserts nothing a regression would break):**

```python
def test_render_invoice():
    invoice = make_invoice(items=3)
    result = render_invoice(invoice)
    assert result is not None          # any non-crashing implementation passes
    assert isinstance(result, str)     # so does one that renders garbage
```

**Correct (names the contract; fails when the contract breaks):**

```python
def test_render_invoice_totals_include_tax():
    invoice = make_invoice(items=[Item(price=100, tax_rate=0.2)])
    result = render_invoice(invoice)
    assert "Total: 120.00" in result   # wrong tax math fails this line
```

Before committing a test, name the contract it defends in the test name. If the honest name is `test_render_invoice_runs`, delete the test — or find the real assertion. Probes written to exercise new code during development are fine as a workflow; the discipline is deleting them before commit instead of promoting them to `skip`, `xfail`, or a literal `assert True`.

### 1.2 Derive Expected Values Independently of the Implementation

**Impact: HIGH (a test that recomputes the code under test proves only self-consistency)**

A test whose expected value is computed by the same logic it's testing proves the code equals itself. When the implementation is wrong, the expectation is wrong the same way, and the test passes. Expected values must come from an independent source: a hand-derived constant, a fixture with known semantics, an invariant that holds regardless of the answer, or a reference implementation that won't share the bug.

**Incorrect (oracle mirrors the implementation):**

```python
def test_shipping_cost():
    order = make_order(weight_kg=12, zone="B")
    expected = BASE_RATE[order.zone] + order.weight_kg * PER_KG[order.zone]  # same formula as the code
    assert shipping_cost(order) == expected
```

If `PER_KG["B"]` is wrong, both sides are wrong together — the test can't notice.

**Correct (hand-derived constant; invariants for the general case):**

```python
def test_shipping_cost_zone_b():
    order = make_order(weight_kg=12, zone="B")
    assert shipping_cost(order) == Decimal("41.80")   # 5.80 base + 12 × 3.00, derived by hand

def test_shipping_cost_monotonic_in_weight():
    light = make_order(weight_kg=1, zone="B")
    heavy = make_order(weight_kg=30, zone="B")
    assert shipping_cost(heavy) > shipping_cost(light)  # holds whatever the rates are
```

The constant came from working the example on paper; the invariant survives rate changes. When a hand-derived value would be brittle (large outputs), assert properties instead: length, ordering, round-trip (`parse(serialize(x)) == x`), or comparison against a trivially-correct reference implementation. Snapshot assertions are a last resort for structured output — they catch *change*, not *correctness*, and every intentional change costs a snapshot review.

### 1.3 One Cohesive Behavior Per Test

**Impact: MEDIUM (a failure names its cause; unrelated phases don't hide behind the first assert)**

A test that bundles independently-failing behaviors reports only the first break: everything after the failing assert is unexercised, so one regression masks another. And the test name stops describing what failed. Split when the phases can fail independently; keep a single test when the asserts describe one cohesive outcome.

**Incorrect (three contracts in a trench coat):**

```python
def test_user_service():
    user = service.create(name="ada")
    assert user.id is not None
    service.rename(user.id, "grace")
    assert service.get(user.id).name == "grace"     # if this fails...
    service.delete(user.id)
    assert service.get(user.id) is None             # ...deletion is never exercised
```

**Correct (each behavior fails under its own name):**

```python
def test_create_assigns_id():
    assert service.create(name="ada").id is not None

def test_rename_persists():
    user = service.create(name="ada")
    service.rename(user.id, "grace")
    assert service.get(user.id).name == "grace"

def test_delete_removes_user():
    user = service.create(name="ada")
    service.delete(user.id)
    assert service.get(user.id) is None
```

Multiple asserts are fine when they describe one outcome (`status == 200` and body shape of the same response). The test is too big when its name needs "and". The inverse discipline: merge tests that assert the *same* contract twice, and delete tests obsoleted by a behavior change — keeping them for test-count or coverage optics preserves numbers, not protection.

## 2. Determinism

**Impact: HIGH**

Tests that pass for reasons. Event-based synchronization over sleeps, strict xfail, no flake-masking retries. Nondeterminism hidden today is a debugging session later.

### 2.1 Fix Nondeterminism, Don't Mask It

**Impact: HIGH (every masking mechanism converts a diagnosable bug into a permanent tax)**

A flaky test is evidence: a race, an order dependency, leaked state, or a timing assumption — in the test or in the code under test. Rerun plugins, widened timeouts, `flaky` markers, and intermittent `xfail` all convert that evidence into permanent noise: the bug stays, the suite slows, and every future flake hides behind the masking already in place. Masking also inverts the incentive — once retries are normal, nobody investigates the first failure.

**Incorrect (each mechanism hides the same unfixed race):**

```python
@pytest.mark.flaky(reruns=3)                    # passes on the third try ≠ passes
def test_cache_eviction(): ...

@pytest.mark.xfail(reason="sometimes fails on CI")   # non-strict: quietly ignores both outcomes
def test_concurrent_writes(): ...

# conftest.py
FLAKY_TIMEOUT = 30  # was 5; raised until CI stopped failing
```

**Correct (make the failure reproducible, then fix the cause):**

```python
def test_cache_eviction():
    clock = FakeClock()                          # control the time the race depended on
    cache = Cache(max_age=60, clock=clock)
    cache.set("k", "v")
    clock.advance(61)
    assert cache.get("k") is None
```

The repair toolkit: control the sources of nondeterminism (inject clocks, seed RNGs, synchronize on events per `determinism-sync-not-sleep`), isolate leaked state (`fixtures-restore-global-state`), and reproduce order dependence by running the failing test alone and with `-p no:randomly` / a fixed seed to bisect. When a fix genuinely can't land now, a *strict, linked* skip is the honest parking spot: `pytest.mark.skip(reason="racy: see ISSUE-123")` — visible, tracked, and not silently consuming retries on every run.

### 2.2 Synchronize on Events, Not Sleeps

**Impact: HIGH (sleeps prove timing luck, and the flakes arrive with CI load)**

A sleep in a concurrency test encodes a bet about scheduling: "0.1 s is enough for the worker to finish." On a loaded CI runner the bet loses, and the test flakes; on every other run the bet wins, and the suite still pays the sleep. Ordering and completion are facts the code under test can expose — synchronize on events, barriers, or observable state transitions, with a bounded timeout as the failure path.

**Incorrect (timing bet):**

```python
async def test_worker_processes_job():
    worker.submit(job)
    await asyncio.sleep(0.1)                 # hope the worker ran
    assert job.id in worker.completed
```

**Correct (synchronize on the observable transition):**

```python
async def test_worker_processes_job():
    done = asyncio.Event()
    worker.on_complete(lambda _: done.set())
    worker.submit(job)
    async with asyncio.timeout(5):           # bound the wait, not the assertion
        await done.wait()
    assert job.id in worker.completed
```

The timeout is generous because it's a *failure bound*, not a performance claim — it only matters when the test is already broken. The same applies to threads (`threading.Event`, `Barrier`) and to polling an observable condition with a deadline when no hook exists. Never assert on elapsed-time thresholds to prove ordering ("the second task finished within 50 ms") — host speed is not part of the contract. If the code under test offers no way to observe completion, that's missing design, and the test just found it.

### 2.3 Use Strict xfail So Unexpected Passes Fail

**Impact: MEDIUM (non-strict xfail silently absorbs both outcomes forever)**

`xfail` marks a test that *should* fail today — a known bug, an unimplemented case. Without `strict=True`, an xfail that unexpectedly passes reports `XPASS` and the run stays green: when the bug gets fixed (or the test stops testing anything), nobody is told, and the marker outlives its reason indefinitely. Strict mode makes the marker self-expiring — the moment reality diverges from the annotation, the suite says so.

**Incorrect (non-strict; both outcomes accepted forever):**

```python
@pytest.mark.xfail(reason="negative quantities not supported yet")
def test_refund_negative_quantity():
    assert refund(make_order(), quantity=-1).status == "rejected"
```

If negative-quantity handling ships, this silently flips to `XPASS` and keeps flipping — the marker never gets cleaned up.

**Correct (strict; an unexpected pass fails the run):**

```python
@pytest.mark.xfail(strict=True, reason="negative quantities not supported yet — ISSUE-482")
def test_refund_negative_quantity():
    assert refund(make_order(), quantity=-1).status == "rejected"
```

When the feature lands, the run fails with `[XPASS(strict)]`, and the fix is to delete the marker — the test graduates to a normal regression test. Set `xfail_strict = true` in project config to make strict the default. Two boundaries to respect: `xfail` documents a *deterministic* known failure, never an intermittent one (that's flake-masking — see `determinism-no-flake-masking`); and neither `xfail` nor `skip` is a parking spot for development probes that never asserted anything (see `value-observable-contracts` — those get deleted).

## 3. Fixtures & Isolation

**Impact: MEDIUM-HIGH**

State that comes back clean. Narrowest fixture scope, restored globals, canonical object construction. Leaked state makes test order a hidden input.

### 3.1 Build Fixture Objects Through Production Constructors

**Impact: MEDIUM (hand-built partial data discovers required fields one failure at a time)**

A fixture assembled as a raw dict or a partially-filled object encodes a guess about what the code under test requires. Each missing field surfaces as a separate test failure — fix `auth`, rerun, discover `region`, rerun — and the finished fixture is a private fork of the schema that silently rots when the real model gains a field. Build fixtures through the same constructor, validator, or factory production code uses, so a fixture that constructs is a fixture that's complete.

**Incorrect (hand-built dict; schema knowledge duplicated and partial):**

```python
@pytest.fixture
def deploy_config():
    return {                                # guessed shape
        "image": "app:1.2.3",
        "replicas": 2,
        # missing "auth" — first failure; missing "region" — second failure
    }
```

**Correct (canonical constructor; defaults centralized in one factory):**

```python
@pytest.fixture
def make_deploy_config():
    def _make(**overrides: object) -> DeployConfig:
        defaults: dict[str, object] = {
            "image": "app:1.2.3",
            "replicas": 2,
            "auth": AuthRef("deploy-bot"),
            "region": "us-east-1",
        }
        return DeployConfig.validate(defaults | overrides)   # production validator fills/checks the rest
    return _make

def test_scale_up(make_deploy_config):
    config = make_deploy_config(replicas=6)
    assert plan(config).action == "scale-up"
```

The factory-fixture pattern gives every test a *complete, valid* object and lets it name only the fields the behavior under test cares about. When the model grows a required field, one factory changes and the suite keeps compiling. Corollary: when a test's setup needs an elaborate web of unrelated-but-required subsystems, that's the fixture telling you the phases are coupled — stub the orthogonal phase behind its interface rather than feeding it ever-more-complete data.

**Exception — the constructor under test:** tests *of* the constructor or validator itself must not route their inputs through it. Feed raw inputs and assert against independently-derived expectations (see `value-independent-oracles`); a validator test whose fixture already passed the validator can only confirm that the validator agrees with itself.

### 3.2 Give Fixtures the Narrowest Safe Scope

**Impact: MEDIUM (shared fixture state makes test order a hidden input)**

A fixture's scope is a sharing contract: `session` scope means every test sees the same object, including mutations left by earlier tests. Widening scope for speed trades isolation for it — and the cost surfaces later as tests that pass alone but fail in suite order (or worse, pass only in suite order). Default to `function` scope; widen only when the fixture is expensive *and* the shared object is immutable or reset between uses.

**Incorrect (session-scoped mutable state — tests now interact):**

```python
@pytest.fixture(scope="session")
def db():
    return InMemoryDB()          # every test shares one instance

def test_create_user(db):
    db.insert(User(name="ada"))
    assert db.count(User) == 1   # passes alone; fails after any test that inserted
```

**Correct (function scope for mutable state; widen only immutable expensive setup):**

```python
@pytest.fixture
def db():
    return InMemoryDB()          # fresh per test — order stops mattering

@pytest.fixture(scope="session")
def compiled_schema() -> Schema:
    return Schema.compile(SCHEMA_PATH)   # expensive, read-only: safe to share
```

A middle path for expensive-but-mutable resources: acquire at `session` scope, reset at `function` scope (truncate tables, clear caches) — the sharing is of the *connection*, not the *state*. Declare fixtures as explicit parameters rather than `autouse=True` where possible; autouse hides a dependency every test silently carries, and hidden dependencies are how "why does this test need a database?" questions start.

### 3.3 Restore Every Mutated Global, Including Absent Ones

**Impact: MEDIUM-HIGH (leaked env vars and registries corrupt every test that runs after)**

Environment variables, the working directory, module-level registries, class attributes, random seeds — anything process-global that a test mutates outlives the test unless something restores it. The next casualty is whichever test runs after, in an order that varies by `-k` filter and parallel worker, which is how "passes alone, fails in CI" is born. Restoration must also cover the *absent* case: a variable that didn't exist before the test must be deleted after, not left set. And it must run on failure, not just success — teardown in the test body after the asserts doesn't.

**Incorrect (manual mutation; leaks on failure; absent var left set):**

```python
def test_uses_staging_endpoint():
    os.environ["API_ENDPOINT"] = "https://staging.example.com"   # never removed
    os.chdir("/tmp/scratch")                                     # leaks to every later test
    assert client().endpoint.startswith("https://staging")
    del os.environ["API_ENDPOINT"]                               # skipped when the assert fails
```

**Correct (`monkeypatch` — undone automatically, on success and failure alike):**

```python
def test_uses_staging_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("API_ENDPOINT", "https://staging.example.com")
    monkeypatch.chdir(tmp_path)
    assert client().endpoint.startswith("https://staging")
```

`monkeypatch` records prior state — including "was not set" — and restores it in teardown regardless of outcome; `tmp_path` gives an isolated directory instead of a shared scratch location. The same applies to registries and class attributes (`monkeypatch.setattr`, `monkeypatch.setitem`) and to hand-rolled fixtures: put the restore in the fixture's teardown (`yield` + `finally`), never in the test body. If a test needs a *clean* environment rather than one extra variable, `monkeypatch.delenv(..., raising=False)` each variable the code reads — inheriting the developer's shell into assertions is its own order dependency.

## 4. Mocking

**Impact: MEDIUM-HIGH**

Fakes that prove something. Mock at owned IO boundaries, patch where names are looked up, assert wire representations. A test fully determined by its mocks tests the mocks.

### 4.1 Assert the Wire Representation, Not the Python Intent

**Impact: MEDIUM (serializers change casing and encoding between your value and the peer)**

Compatibility with an external system lives at the serialized boundary — the query string, the JSON bytes, the header line — not at the Python value you intended to send. Serializers make their own choices on the way out: `urlencode({"include_disabled": False})` produces `include_disabled=False` (capital F), which a server comparing against `"false"` rejects; `json.dumps` and datetime/decimal encoders make similar choices. A test that asserts the Python-level argument can pass while every real request fails.

**Incorrect (asserts intent; encoding never checked):**

```python
def test_list_users_excludes_disabled(fake_transport):
    client.list_users(include_disabled=False)
    assert fake_transport.last_request.params == {"include_disabled": False}
    # urlencode sent "include_disabled=False"; the server expected "false" — test can't see it
```

**Correct (asserts the serialized boundary the peer actually parses):**

```python
def test_list_users_excludes_disabled(fake_transport):
    client.list_users(include_disabled=False)
    assert fake_transport.last_request.url.query == "include_disabled=false"

def test_create_user_body_wire_format(fake_transport):
    client.create_user(name="Ada", joined=date(2026, 3, 1))
    assert fake_transport.last_request.body == b'{"name": "Ada", "joined": "2026-03-01"}'
```

If the exact byte string is too brittle, parse the wire form back and assert on the parsed *strings* (`parse_qs(query)["include_disabled"] == ["false"]`) — still the peer's view, minus ordering sensitivity. The principle generalizes: whenever a test guards compatibility with a system that parses text or bytes, the assertion belongs on the text or bytes. This is also why `mock-stable-boundaries` fakes the transport rather than the client — mock the client and there is no wire representation left to assert on.

### 4.2 Mock at Stable IO Boundaries, Not the Behavior Under Test

**Impact: MEDIUM-HIGH (a test fully determined by its mocks is tautological)**

Every mock removes real behavior from the test. Mock the whole client and the test exercises none of the request encoding, response parsing, or error mapping the client wraps — the assertions check that the mock returns what the mock was told to return. Fake only the boundary you don't own (the network transport, the clock, the filesystem), and let everything you *do* own run for real. Prefer a cheap real collaborator — an in-memory repository, a real parser on canned bytes — over a broad `MagicMock` whose behavior is whatever the test wishes.

**Incorrect (mocked the code under test; tautology):**

```python
def test_fetch_user(mocker):
    api = mocker.patch("app.service.ApiClient")            # entire client replaced
    api.return_value.get_user.return_value = User(id="u1")
    assert get_user_profile("u1").id == "u1"               # asserts the mock echoed itself
```

Encoding, parsing, auth headers, and error mapping are all unexercised — a broken `ApiClient` passes.

**Correct (real client; fake transport at the boundary):**

```python
def test_fetch_user_parses_response(fake_transport):
    fake_transport.enqueue(200, body=b'{"id": "u1", "name": "Ada"}')
    client = ApiClient(transport=fake_transport)           # real encoding + parsing run
    user = get_user_profile("u1", client=client)
    assert user.name == "Ada"
    assert fake_transport.last_request.url.path == "/users/u1"
```

Now request construction and response parsing are under test; only the socket is fake. The litmus: could this test fail if the production code (not the test) had a bug? If every assertion is satisfied by construction of the mocks, the answer is no. And when a fake drifts from the real API's shape, update the fake — adding compatibility shims to production code so old fakes keep passing inverts the relationship entirely.

### 4.3 Patch Where the Name Is Looked Up, Not Where It's Defined

**Impact: MEDIUM-HIGH (a patch at the definition site silently misses the import already taken)**

`from payments.gateway import charge` copies the function reference into the importing module's namespace at import time. Patching `payments.gateway.charge` afterwards rebinds the *original* module's name — the copy in the module under test still points at the real function, and the test either hits the network or asserts against a mock that was never called. Patch the name in the namespace where the code under test looks it up.

**Incorrect (patched the definition site; the copy is untouched):**

```python
# app/checkout.py
from payments.gateway import charge

def submit_order(order: Order) -> Receipt:
    return charge(order.total)

# tests/test_checkout.py
def test_submit_order(mocker):
    fake = mocker.patch("payments.gateway.charge")   # checkout.charge still the real one
    submit_order(make_order())
    fake.assert_called_once()                        # AssertionError: not called
```

**Correct (patch the lookup site):**

```python
def test_submit_order(mocker):
    fake = mocker.patch("app.checkout.charge", return_value=Receipt(ok=True))
    submit_order(make_order())
    fake.assert_called_once()
```

The rule falls out of Python's name binding, so the *code style* determines the patch target: code that does `import payments.gateway` and calls `payments.gateway.charge(...)` looks the name up on the module object at call time, so patching `payments.gateway.charge` works from anywhere. Either way, the question to ask is "which namespace does the code under test read this name from at call time?" — patch that one. (This is the mechanics rule; whether the boundary *should* be mocked at all is `mock-stable-boundaries`.)

## 5. Structure & Execution

**Impact: MEDIUM**

The suite as a system. Contract-distinct parametrization, collision-free module identities, deliberate plugin surface, preserved exit codes. Collection-time and CI-time failure modes live here.

### 5.1 Keep Test Module Import Identities Collision-Free

**Impact: LOW-MEDIUM (same-named test modules pass separately and fail when suites compose)**

Under pytest's default `prepend` import mode, a test module in a non-package directory imports under its bare filename: `service/tests/test_utils.py` and `scripts/tests/test_utils.py` both claim the import name `test_utils`. Collect either tree alone and it passes; collect both in one invocation and pytest raises `ImportPathMismatchError` (or one module shadows the other). The failure appears exactly when suites compose — the combined CI run breaks while every per-project run stays green.

**Incorrect (two non-package trees claim one import identity):**

```
service/tests/test_utils.py      # imports as "test_utils"
scripts/tests/test_utils.py      # also "test_utils" → ImportPathMismatchError when both collect
```

**Correct (unique identities — packaged trees, or unique filenames):**

```
service/tests/__init__.py        # modules import as "service.tests.*"
service/tests/test_service_utils.py
scripts/tests/__init__.py        # distinct package: "scripts.tests.*"
scripts/tests/test_script_utils.py
```

Three ways out, pick one per repository: add `__init__.py` so test trees are packages with distinct package-qualified names; keep flat un-packaged trees but give test modules globally-unique filenames; or set `--import-mode=importlib`, which pytest recommends for new projects and which removes the uniqueness requirement altogether. Per-directory `conftest.py` files are unaffected — many conftests with the same filename are normal, supported pytest design. Naming test modules after what they test (`test_billing_rounding.py`, not a third `test_utils.py`) sidesteps the collision and reads better in failure output anyway.

### 5.2 Make the Plugin Surface Explicit When Autoload Bites

**Impact: LOW-MEDIUM (uninvited plugins change suite behavior when unrelated dependencies bump)**

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

Diagnose with `pytest --trace-config` (lists every active plugin) or compare a run with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` plus explicit `-p` flags for the plugins the suite actually uses — the allowlist form, which makes the whole surface declared rather than inherited. Symptoms that warrant the audit: collection noticeably slower than test time, retries or telemetry no config requested, tests behaving differently on one machine. Plugins the suite genuinely depends on belong in dev dependencies by name; leaving autoload alone in the absence of symptoms is a fine default, not a violation.

### 5.3 Parametrize Contract-Distinct Partitions

**Impact: MEDIUM (cases that differ only in data restate one partition; cases that hide logic obscure many)**

`parametrize` earns its keep when each case is a distinct partition of the input space with an independently-derived expected result — boundary, typical, degenerate, error. Ten cases that exercise the same partition with different literals add runtime and noise, not protection; and a parametrized test whose body branches on the case (`if expected_error: ... else: ...`) has grown two tests wearing one name.

**Incorrect (same partition five times; body branches per case):**

```python
@pytest.mark.parametrize("a, b", [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])  # all "two positives"
def test_add(a, b):
    assert add(a, b) == a + b            # oracle mirrors the implementation, too

@pytest.mark.parametrize("value, should_raise", [(5, False), (-1, True)])
def test_set_limit(value, should_raise):
    if should_raise:                     # two contracts sharing a name
        with pytest.raises(ValueError):
            set_limit(value)
    else:
        assert set_limit(value) == 5
```

**Correct (named partitions, independent expecteds; error cases stand alone):**

```python
@pytest.mark.parametrize(
    "quantity, expected",
    [
        pytest.param(1, Decimal("9.99"), id="single-item"),
        pytest.param(12, Decimal("107.89"), id="dozen-crosses-discount-threshold"),
        pytest.param(0, Decimal("0"), id="empty-order"),
    ],
)
def test_order_total(quantity, expected):
    assert order_total(make_order(quantity=quantity)) == expected

def test_set_limit_rejects_negative():
    with pytest.raises(ValueError, match="must be positive"):
        set_limit(-1)
```

`id=` names make a failing case self-describing in the report. When case lists are generated, guard the degenerate outcome: an accidentally-empty parameter set skips silently by default — set `empty_parameter_set_mark = fail_at_collect` so a filter bug that produces zero cases fails collection instead of green-lighting nothing.


## References

- https://docs.pytest.org/en/stable/
- https://docs.pytest.org/en/stable/explanation/goodpractices.html
- https://docs.pytest.org/en/stable/how-to/fixtures.html
- https://docs.pytest.org/en/stable/how-to/monkeypatch.html
- https://docs.pytest.org/en/stable/how-to/parametrize.html
- https://docs.pytest.org/en/stable/how-to/skipping.html
- https://docs.pytest.org/en/stable/how-to/flaky.html
- https://docs.python.org/3/library/unittest.mock.html#where-to-patch
- https://docs.python.org/3/library/asyncio-sync.html
