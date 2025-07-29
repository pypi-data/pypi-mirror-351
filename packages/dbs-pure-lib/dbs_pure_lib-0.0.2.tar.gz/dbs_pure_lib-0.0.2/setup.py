from setuptools import setup




setup(
    name='dbs_pure_lib',
    version='0.0.2',
    packages=['dbs_image_utils'],
    description='DBS Image Utilities',
    long_description=open("README.md").read(),
    install_requires=['torch','nibabel'],
    url='',
    license='',
    author='igor_varha',
    author_email='ivarhauzh@gmail.com',
)
