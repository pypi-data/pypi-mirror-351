from setuptools import setup
from setuptools.command.install import install
import os

class CustomInstall(install):
    def run(self):
        # Create the file in /tmp
        open('/tmp/azure-projects', 'a').close()
        print("Created /tmp/azure-projectsc during installation")
        # Run the standard install
        install.run(self)

setup(
    name='azure-projects',
    version='0.1a0',
    description='Test package that creates a file on install in /tmp direcotyr',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='secangel',
    cmdclass={
        'install': CustomInstall,
    },
)
