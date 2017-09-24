from setuptools import setup


setup(
    name='automator',
    version='0.0.1',
    description='Automator for shell control',
    install_requires=[
        'paramiko',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
