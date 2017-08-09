from setuptools import setup


setup(
    name='automator',
    version='0.0.1',
    description='Automator for shell control (and testing)',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
