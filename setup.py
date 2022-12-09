from setuptools import setup, find_packages
import versioneer


versioneer.VCS = 'git'
versioneer.versionfile_source = 'magicplot/_version.py'
versioneer.versionfile_build = 'magicplot/_version.py'
versioneer.tag_prefix = '' # tags are like 1.2.0
versioneer.parentdir_prefix = 'magicplot-' # dirname like 'myproject-1.2.0'


setup(
    name='magicplot',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Oliver Farley',
    author_email='o.j.d.farley@durham.ac.uk',
    packages=['magicplot', 
            'magicplot.plugins',
            'magicplot.plugins.analysis',
            'magicplot.plugins.transforms'
        ],
    scripts=[],
    description='A Generalised Plotting Tool for Science',
    long_description=open('README.md').read(),
    package_data={'magicplot': ['*.ui']},
    include_package_data=True

)
