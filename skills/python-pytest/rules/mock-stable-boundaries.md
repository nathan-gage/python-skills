---
title: Mock at Stable IO Boundaries, Not the Behavior Under Test
impact: MEDIUM-HIGH
impactDescription: a test fully determined by its mocks is tautological
tags: mock, boundaries, fakes
references: https://docs.python.org/3/library/unittest.mock.html, https://docs.pytest.org/en/stable/how-to/monkeypatch.html
---

## Mock at Stable IO Boundaries, Not the Behavior Under Test

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
