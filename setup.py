from setuptools import setup, find_packages

setup(
    name="mailmaestro",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # See requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "mail-maestro = mail_maestro.main:cli",
        ],
    },
    author="Ibrahim Abouhashish",
    description="An extensible, multi-pipeline email automation agent",
    license="MIT",
)
