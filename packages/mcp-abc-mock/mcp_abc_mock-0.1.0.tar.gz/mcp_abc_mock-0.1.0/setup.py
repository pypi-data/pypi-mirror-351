from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

setup(
    name="mcp-abc-mock",  # Must be globally unique on PyPI
    version="0.1.0",
    author="Kyle Fang",
    author_email="kfang01@amgen.com",
    description="Mock MCP server tools for ABC model context protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(
        include=["mcp_abc_mock", "mcp_abc_mock.*"],
        exclude=["test_code"],
    ),
    include_package_data=True,
    package_data={
        "mcp_abc_mock": ["fake_abc_data.csv"],
    },
    install_requires=(this_directory / "requirements.txt").read_text().splitlines(),
    classifiers=[],
    python_requires=">=3.7",
)
