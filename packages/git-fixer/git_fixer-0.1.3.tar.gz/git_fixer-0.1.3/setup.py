from setuptools import setup, find_packages
import os

# Read the long description from README.md
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="git-fixer",
    version="0.1.3",
    description="Generate fake git commits to create realistic GitHub activity graphs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dev Vyas",
    author_email="devvyas17272@gmail.com",
    url="https://github.com/SirNosh/git-fixer",
    license="MIT",
    packages=["git_fixer", "git_fixer.src"],
    package_dir={"": "."},
    entry_points={
        "console_scripts": [
            "git-fixer=git_fixer.src.fake_git_history:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    keywords="git, github, contribution, activity, commit, history",
    python_requires=">=3.6",
) 