from setuptools import find_packages, setup

setup(
    name='flask-redis-lib',
    packages=find_packages(),
    version='0.1',  # Increment version
    description='A specialized library for efficient Redis caching in Flask applications.',
    author='Mohan',
    author_email='mohagude5@gmail.com',
    install_requires=["redis==5.2.0", "Flask>=3.0.3"],
    maintainer='Mohan',
    maintainer_email='mohangude5@gmail.com'
)
