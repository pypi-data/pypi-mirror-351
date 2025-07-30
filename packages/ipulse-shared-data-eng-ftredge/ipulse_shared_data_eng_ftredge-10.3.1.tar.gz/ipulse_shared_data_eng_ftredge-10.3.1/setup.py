# pylint: disable=import-error
from setuptools import setup, find_packages

setup(
    name='ipulse_shared_data_eng_ftredge',
    version='10.3.1',
    package_dir={'': 'src'},  # Specify the source directory
    packages=find_packages(where='src'),  # Look for packages in 'src'
    install_requires=[
        # List your dependencies here
        'python-dateutil~=2.9.0',
        'pytest~=7.1',
        'Cerberus~=1.3.5',
        'ipulse_shared_base_ftredge~=7.2.0', ##contains google cloud logging and error reporting
        'google-cloud-bigquery~=3.29.0',
        'google-cloud-storage~=3.0.0',
        'google-cloud-pubsub~=2.28.0',
        'google-cloud-secret-manager~=2.22.0',
        'google-cloud-firestore~=2.20.0',
        
    ],
    author='Russlan Ramdowar',
    description='Shared Data Engineering functions for the Pulse platform project. Using AI for financial advisory and investment management.',
    url='https://github.com/TheFutureEdge/ipulse_shared_data_eng'
)
