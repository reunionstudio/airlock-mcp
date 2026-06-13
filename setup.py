from glob import glob
from os.path import isfile

from setuptools import find_packages, setup


def data_files():
    files = [
        (
            "airlock_mcp/.agents/skills/airlock-mcp",
            [path for path in glob(".agents/skills/airlock-mcp/*") if isfile(path)],
        ),
        (
            "airlock_mcp/.agents/skills/airlock-mcp/agents",
            [path for path in glob(".agents/skills/airlock-mcp/agents/*") if isfile(path)],
        ),
        ("airlock_mcp/patterns", ["patterns/manifest.json"]),
        ("airlock_mcp/workspaces/_template", glob("workspaces/_template/*")),
    ]
    for pattern_dir in glob("patterns/*"):
        if pattern_dir.endswith("manifest.json"):
            continue
        if glob(f"{pattern_dir}/*"):
            files.append((f"airlock_mcp/{pattern_dir}", glob(f"{pattern_dir}/*")))
    return files


setup(
    name="airlock-mcp",
    version="0.1.2",
    description="Codex-first workbench and CLI for drafting Airlock specs.",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    data_files=data_files(),
    entry_points={
        "console_scripts": [
            "airlock-mcp=airlock_mcp.cli:main",
        ],
    },
)
