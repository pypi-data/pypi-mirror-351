import setuptools

setuptools.setup(
    name='ubuntu-release-names',
    version="1.0.0",
    author='@readwithai',
    long_description_content_type='text/markdown',
    author_email='talwrii@gmail.com',
    description='Fetch the current ubuntu release names and versions from wikipedia',
    license='GPLv3',
    keywords='ubuntu,release,versios',
    url='',
    install_requires=["lxml"],
    packages=["ubuntu_release_names"],
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['ubuntu-release-names=ubuntu_release_names.main:main']
    }
)
