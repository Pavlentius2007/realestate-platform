#!/usr/bin/env python3
"""
Setup script для транскрибатора
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()

# Читаем requirements
requirements_path = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                install_requires.append(line)

setup(
    name="audio-transcriber",
    version="1.0.0",
    author="Transcriber Team",
    author_email="info@transcriber.com",
    description="Программа для транскрибации аудиофайлов в текст",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/audio-transcriber",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "transcriber=transcriber:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="audio transcription whisper speech-to-text",
    project_urls={
        "Bug Reports": "https://github.com/your-username/audio-transcriber/issues",
        "Source": "https://github.com/your-username/audio-transcriber",
        "Documentation": "https://github.com/your-username/audio-transcriber#readme",
    },
) 