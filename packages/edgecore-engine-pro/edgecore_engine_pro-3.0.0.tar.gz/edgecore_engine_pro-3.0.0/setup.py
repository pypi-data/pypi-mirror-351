from setuptools import setup, find_packages

setup(
    name="edgecore_engine_pro",
    version="3.0.0",
    description="EdgeCore 3.0 Production Engine",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "torch==2.1.0+cpu",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "edgecore-pro = edgecore_engine_pro.core:main",
        ],
    },
)
