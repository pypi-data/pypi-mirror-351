from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='source2prompt',
    version='0.2.3',
    packages=['source2prompt'],
    entry_points={
        'console_scripts': [
            's2p=source2prompt:main'
        ]
    },
    install_requires=[
        'charset_normalizer',
    ],
    author='IchigoHydrogen',
    description='A simple tool to convert source files to a single prompt file for LLMs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/IchigoHydrogen/source2prompt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    include_package_data=True,
)