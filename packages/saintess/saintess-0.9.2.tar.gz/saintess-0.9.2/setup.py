from setuptools import setup, find_packages

setup(
    name="saintess",
    version="0.9.2",
    packages=find_packages(),
    install_requires=["discord.py"],
    author="Saint Official",
    author_email="support@saint.xxx",
    description="Official wrapper for Discord API.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/saintess",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
)
