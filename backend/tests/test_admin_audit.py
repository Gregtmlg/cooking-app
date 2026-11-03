"""Journal d'audit du back-office : les refus sont journalisés autant que les succès."""

ADMIN = "/api/v1/admin"


def _events(app_logs, name):
    return [r for r in app_logs.records if r.getMessage() == name]


def test_non_admin_on_admin_route_is_logged(auth_client, app_logs):
    auth_client.get(f"{ADMIN}/inventory")

    events = _events(app_logs, "auth.admin_forbidden")
    assert len(events) == 1
    assert events[0].username == "Louise"
    assert events[0].path == f"{ADMIN}/inventory"
    assert events[0].method == "GET"


def test_admin_itself_is_not_flagged(admin_client, app_logs):
    admin_client.get(f"{ADMIN}/inventory")
    assert _events(app_logs, "auth.admin_forbidden") == []


def test_refused_domain_error_is_logged(admin_client, account, app_logs):
    """Erreur métier traduite par _http_error (409) → admin.action_refused."""
    admin_client.post(f"{ADMIN}/accounts", json={"username": "LOUISE", "password": "x" * 8})

    events = _events(app_logs, "admin.action_refused")
    assert len(events) == 1
    assert events[0].action == "account_created"
    assert events[0].status == 409
    assert events[0].actor_username == "Admin"
    assert events[0].target_username == "LOUISE"
    assert _events(app_logs, "admin.account_created") == []  # pas de faux succès


def test_refused_not_found_is_logged(admin_client, app_logs):
    """404 levé par _account_or_404, DANS le bloc → couvert aussi."""
    admin_client.post(f"{ADMIN}/accounts/9999/reset-password", json={"password": "x" * 8})

    events = _events(app_logs, "admin.action_refused")
    assert len(events) == 1
    assert events[0].action == "password_reset"
    assert events[0].status == 404
    assert events[0].target_account_id == 9999


def test_successful_action_logs_no_refusal(admin_client, app_logs):
    admin_client.post(f"{ADMIN}/accounts", json={"username": "Paul", "password": "x" * 8})
    assert len(_events(app_logs, "admin.account_created")) == 1
    assert _events(app_logs, "admin.action_refused") == []


def test_refusal_never_logs_the_password(admin_client, account, app_logs):
    admin_client.post(
        f"{ADMIN}/accounts", json={"username": "LOUISE", "password": "secret-refus-123"}
    )
    for record in app_logs.records:
        assert "secret-refus-123" not in str(vars(record))
