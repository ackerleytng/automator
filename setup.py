from setuptools import setup

test_deps = [
    'pytest',
]
extras = {
    'test': test_deps,
}

setup(
    name='pynomator',
    version='0.0.1',
    description='An intuitive shell automation tool',
    install_requires=[
        'paramiko',
        'ptyprocess',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=test_deps,
    extras_require=extras,
)
