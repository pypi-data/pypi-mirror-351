from setuptools import setup, find_packages

setup(
    name='budgetingcli',
    version='0.1.0',
    author='Your Name',
    description='A CLI tool to track spending goals and habits',
    packages=find_packages(),
    install_requires=[
        'click',
        'rich',
        'ollama',
        'platformdirs'
    ],
    entry_points={
        'console_scripts': [
            'budgetingcli=budgetcli.cli:cli',  # entrypoint to your CLI
        ],
    },
    include_package_data=True,
    python_requires='>=3.8',
)
