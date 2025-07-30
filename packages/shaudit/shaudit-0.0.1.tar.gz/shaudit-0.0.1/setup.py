from setuptools import setup, find_packages

setup(
    name='shaudit',
    version='0.0.1',
    author="invisiber",
    description="Security Headers Audit Tool",
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "argparse",
        "requests",
        "urllib3",
    ],
    entry_points={
        "console_scripts":[
            "shaudit = shaudit.main:main",
        ],
    },
    python_requires=">=3.6",
)
