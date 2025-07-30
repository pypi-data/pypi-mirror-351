from setuptools import setup, find_packages
setup(
    name='pixegami_hello_arya3',
    version='0.2.0',
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