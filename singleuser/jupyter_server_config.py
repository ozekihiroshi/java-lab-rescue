c.ServerProxy.servers = {
    "ide": {
        "command": [
            "code-server", "--bind-addr", "127.0.0.1:{port}", "--auth", "none",
            "--disable-telemetry", "--disable-update-check", "--disable-workspace-trust",
            "--extensions-dir", "/opt/java-extensions",
            "--user-data-dir", "/home/jovyan/work/.ide",
            "/home/jovyan/work/java-intro/course-v1/lesson-00",
        ],
        "timeout": 90,
        "launcher_entry": {"title": "Java IDE"},
    }
}
