from setuptools import setup, find_packages


setup(
    name="imgzen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python"
    ],
    author="<NAME>",
    desciption="Imgzen Python package",
    long_description=open("README.md").read(),
    url="https://github.com/yehorn0/imgzen",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "imgzen = imgzen.main:main"
        ]
    }
)
