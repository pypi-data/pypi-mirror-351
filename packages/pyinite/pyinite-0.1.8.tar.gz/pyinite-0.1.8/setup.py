from setuptools import setup, find_packages

setup(
    name='pyinite',
    version='0.1.8',
    description='A Python lib you can use to initialize your Python scripts (Console based / Windowed)',
    author='Guillaume Plagier',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'pyinitialyze': ['Dll/win32dll.exe']
    },
)
