from setuptools import setup, find_packages

setup(
    name="pyorbbec",
    version="2.4.3",
    description="Your package description",
    author="alvisli",
    author_email="605633002@qq.com",
    url="https://orbbec.com.cn/",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests",  # 举例：你的依赖
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
