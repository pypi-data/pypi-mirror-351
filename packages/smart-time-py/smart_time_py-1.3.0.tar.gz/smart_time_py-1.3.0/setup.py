from setuptools import find_packages, setup

setup(
    name="smart_time_py",
    version="1.3.0",
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="⏳ Uma biblioteca avançada para manipulação de datas e tempos em Python",  # noqa: E501
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/smart-time-py",
    packages=find_packages(),
    install_requires=[
        "pytest>=6.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    license="MIT",
    project_urls={
        "Homepage": "https://github.com/robertolima-dev/smart-time-py", # noqa501
        "Repository": "https://github.com/robertolima-dev/smart-time-py", # noqa501
        "Issues": "https://github.com/robertolima-dev/smart-time-py/issues", # noqa501
    },
)
