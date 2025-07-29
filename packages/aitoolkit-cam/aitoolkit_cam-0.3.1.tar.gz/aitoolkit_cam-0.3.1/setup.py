from setuptools import setup, find_packages

setup(
    name="aitoolkit_cam",
    version="0.3.1",
    author="aitoolkit_cam",
    author_email="",
    description="简单易用的摄像头工具包，支持本地显示和网页流",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aitoolkit_cam",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "flask>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "aitoolkit-cam=aitoolkit_cam.camera:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 