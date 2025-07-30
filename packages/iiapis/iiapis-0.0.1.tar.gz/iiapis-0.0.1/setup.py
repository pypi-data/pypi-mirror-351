from setuptools import setup, find_packages

_name = "iiapis"

setup(
    name=_name,
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'numpy>=1.20.0',
    ],
    author="lqxnjk",
    author_email="lqxnjk@qq.com",
    description="A short description of your package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url=f"https://github.com/lqxnjk/{_name}",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
