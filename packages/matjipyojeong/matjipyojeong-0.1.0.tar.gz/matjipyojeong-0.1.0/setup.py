from setuptools import setup, find_packages

setup(
    name="matjipyojeong",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas"
    ],
    author="Bonitabueno",
    description="지역 기반 식당 검색을 위한 파이썬 라이브러리",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
