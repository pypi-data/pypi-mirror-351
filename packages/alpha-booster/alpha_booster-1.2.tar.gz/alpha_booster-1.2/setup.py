from setuptools import setup, find_packages

setup(
    name="alpha-booster",
    version="1.2",
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama"
    ],
    entry_points={
        'console_scripts': [
            'discord_booster=discord_booster:main',
        ],
    },
)
