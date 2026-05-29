from pathlib import Path


def test_backend_modules_do_not_make_raw_clash_requests():
    project_root = Path(__file__).resolve().parents[1]
    allowed = {
        project_root / "clash_http_client.py",
    }
    offenders = []

    for directory_name in ("api", "services"):
        for path in (project_root / directory_name).glob("*.py"):
            if path in allowed:
                continue
            content = path.read_text()
            if "requests.get(" in content or "requests.post(" in content:
                offenders.append(path.relative_to(project_root).as_posix())

    assert offenders == []
