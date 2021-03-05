from setuptools import setup

setup(
    name='easypyvmomi',
    version='0.0.1',
    description='An easy wrapper for pyvmomi',
    url='https://github.com/atorrescogollo/easypyvmomi',
    author='Álvaro Torres Cogollo',
    author_email='atorrescogollo@gmail.com',
    license='BSD 3-clause',
    packages=['easypyvmomi'],
    install_requires=['requests','pyvmomi'],
    classifiers=[],
)
