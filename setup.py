from setuptools import setup

test_deps = [
    'pytest',
]
extras = {
    'test': test_deps,
}

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
    tests_require=test_deps,
    extras_require=extras,
)
