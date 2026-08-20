---
title: Assert the Wire Representation, Not the Python Intent
impact: MEDIUM
impactDescription: serializers change casing and encoding between your value and the peer
tags: mock, serialization, boundaries
references: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode
---

## Assert the Wire Representation, Not the Python Intent

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

**Scope:** assert exact bytes only where the bytes *are* the contract — signatures, canonical serialization, cache keys, golden protocol fixtures. Otherwise parse the wire form back and assert on the parsed *strings* (`parse_qs(query)["include_disabled"] == ["false"]`) — still the peer's view, minus ordering sensitivity. The principle generalizes: whenever a test guards compatibility with a system that parses text or bytes, the assertion belongs on the text or bytes. This is also why `mock-stable-boundaries` fakes the transport rather than the client — mock the client and there is no wire representation left to assert on.
