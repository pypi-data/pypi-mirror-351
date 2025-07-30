from setuptools import setup, find_packages

setup(
    name="py-ark-vrf",
    packages=find_packages(),
    package_data={
        "py_ark_vrf": ["*.srs"],
    },
    include_package_data=True,
    python_requires=">=3.7",
) 