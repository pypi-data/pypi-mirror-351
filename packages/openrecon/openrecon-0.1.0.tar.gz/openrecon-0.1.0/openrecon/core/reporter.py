from pathlib import Path

def get_reports_dir():
    """Get the path to the reports directory in user's Documents folder"""
    docs_dir = Path.home() / "Documents"
    reports_dir = docs_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    return reports_dir