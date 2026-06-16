"""Kiem tra nhanh cac API chinh."""
import json
import sys

from app import create_app


def login(client, email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed {email}: {res.get_data(as_text=True)}"
    return res.get_json()["access_token"]


def get(client, path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.get(path, headers=headers)


def run():
    app = create_app()
    failures = []
    passed = 0

    with app.test_client() as client:
        tests = [
            ("GET", "/api/health", None, 200),
            ("GET", "/api/homepage", None, 200),
            ("GET", "/api/courses", None, 200),
            ("GET", "/api/news", None, 200),
            ("GET", "/api/seo/home", None, 200),
        ]

        for method, path, token, expected in tests:
            res = get(client, path, token) if method == "GET" else client.post(path)
            ok = res.status_code == expected
            if ok:
                passed += 1
            else:
                failures.append(f"{method} {path} -> {res.status_code} (expected {expected})")

        for role, email, password in [
            ("admin", "admin@vuquyenamerican.com", "admin123"),
            ("teacher", "teacher@vuquyenamerican.com", "teacher123"),
            ("student", "student@vuquyenamerican.com", "student123"),
        ]:
            token = login(client, email, password)
            role_tests = {
                "admin": [
                    "/api/dashboard/admin",
                    "/api/users/teachers",
                    "/api/users/students?page=1",
                    "/api/classes",
                    "/api/seo",
                ],
                "teacher": [
                    "/api/dashboard/teacher",
                    "/api/classes",
                    "/api/quizzes",
                    "/api/video-lessons",
                    "/api/documents",
                ],
                "student": [
                    "/api/dashboard/student",
                    "/api/quizzes",
                    "/api/video-lessons",
                    "/api/documents",
                ],
            }
            for path in role_tests[role]:
                res = get(client, path, token)
                if res.status_code == 200:
                    passed += 1
                    try:
                        res.get_json()
                    except Exception as e:
                        failures.append(f"GET {path} ({role}) JSON error: {e}")
                else:
                    failures.append(f"GET {path} ({role}) -> {res.status_code}: {res.get_data(as_text=True)[:200]}")

        # Student quiz flow
        student_token = login(client, "student@vuquyenamerican.com", "student123")
        quizzes = get(client, "/api/quizzes", student_token).get_json()
        if quizzes.get("items"):
            qid = quizzes["items"][0]["_id"]
            res = get(client, f"/api/quizzes/{qid}", student_token)
            if res.status_code == 200:
                passed += 1
            else:
                failures.append(f"GET /api/quizzes/{qid} -> {res.status_code}")

        videos = get(client, "/api/video-lessons", student_token).get_json()
        if videos.get("items"):
            vid = videos["items"][0]["_id"]
            res = get(client, f"/api/video-lessons/{vid}?include_quiz=true", student_token)
            if res.status_code == 200:
                passed += 1
            else:
                failures.append(f"GET /api/video-lessons/{vid} -> {res.status_code}")

    print(f"\nPassed: {passed}")
    if failures:
        print(f"Failed: {len(failures)}")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All API checks passed!")
    sys.exit(0)


if __name__ == "__main__":
    run()
