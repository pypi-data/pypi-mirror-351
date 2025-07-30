from setuptools import setup, find_packages
setup(
    name='pixegami_hello_arya2',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
          # Ensure this matches the version of pixegami you are using
    ],

    entry_points={
        "console_scripts": [
            "charan-hello=pixegami_hello:hello",
        ],
    }
)