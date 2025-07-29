from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

setup(
    name="mcp-psilo-mock",  # Must be globally unique on PyPI
    version="0.1.18",
    author="Kyle Fang",
    author_email="kfang01@amgen.com",
    description="Mock MCP server tools for psilo model context protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.nimbus.amgen.com/xai/mcp_psilo",
    packages=find_packages(
        include=["mcp_psilo_mock", "mcp_psilo_mock.*"],
        exclude=["mcp_psilo_in_progress", "mcp_psilo_in_progress*", "test_code"],
    ),
    include_package_data=True,
    package_data={
        "mcp_psilo_mock": ["fake_psilo_data.csv"],
    },
    install_requires=(this_directory / "requirements.txt").read_text().splitlines(),
    classifiers=[],
    python_requires=">=3.7",
)
