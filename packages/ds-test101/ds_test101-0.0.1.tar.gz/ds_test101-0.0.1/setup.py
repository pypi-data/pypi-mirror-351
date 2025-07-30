import setuptools

setuptools.setup(
    # pip3 install test-lib
    name="ds-test101", # Replace with your own username
    version="0.0.1",
    author="Tito",
    author_email="author@example.com",
    description="A small example package",
    long_description_content_type="text/markdown",
    url="https://github.com/Tester-Dss/Hello-101.git",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
