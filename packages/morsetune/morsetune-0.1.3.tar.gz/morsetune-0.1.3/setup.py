import setuptools

def readme():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
    name="morsetune",
    version="0.1.3",
    description="Convert text to its corresponding Morse Code tune.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Samuel Zhang",
    author_email="qisamuelzhang@hotmail.com",
    url="https://github.com/yiyitech/morsetune",
    license="MIT",
    packages=["morsetune"],
    test_suite="nose.collector",
    tests_require=[
        "nose"
    ],
    setup_requires=[
        "numpy"
    ],
    install_requires=[
        "numpy"
    ],
)