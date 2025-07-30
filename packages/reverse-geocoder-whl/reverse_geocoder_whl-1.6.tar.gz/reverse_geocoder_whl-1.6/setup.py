import pathlib

import setuptools


PYPI_NAME = "reverse-geocoder-whl".replace("-", "_")
MODULE_NAME = PYPI_NAME.replace("-", "_")
EXT_SRC = pathlib.Path("c++") / "lib"

EXT_SOURCE_FILES = [
    str(p)
    for ext in ("c", "cpp")
    for p in EXT_SRC.glob(f"**/*.{ext}")
]

ext_modules = [
    setuptools.Extension(
        name=MODULE_NAME,
        # Sort input source files to ensure bit-for-bit reproducible builds
        sources=sorted(EXT_SOURCE_FILES),
    ),
]


setuptools.setup(
    name=PYPI_NAME,
    url='https://github.com/TalAmuyal/reverse-geocoder-whl',
    packages=setuptools.find_packages(),
    package_dir={'reverse_geocoder_whl': f"./{MODULE_NAME}"},
    package_data={'reverse_geocoder_whl': ['rg_cities1000.csv']},
    ext_modules=ext_modules,
)
