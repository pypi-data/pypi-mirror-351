from setuptools import setup, find_packages

setup(
    name="youtupy",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "clight",
        "yt-dlp",
        "imageio-ffmpeg",
        "yt_dlp",
        "imageio_ffmpeg"
    ],
    entry_points={
        "console_scripts": [
            "youtupy=youtupy.main:main",  # Entry point of the app
        ],
    },
    package_data={
        "youtupy": [
            "main.py",
            "__init__.py",
            ".system/imports.py",
            ".system/index.py",
            ".system/modules/-placeholder",
            ".system/sources/chars.yml",
            ".system/sources/clight.json",
            ".system/sources/logo.ico"
        ],
    },
    include_package_data=True,
    author="Irakli Gzirishvili",
    author_email="gziraklirex@gmail.com",
    description="Download videos from YouTube",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/IG-onGit/YouTuPy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
