from setuptools import setup, find_packages


long_description = """
snowfuse is a security-focused Python library built on top of FUSE (Filesystem in Userspace) that 
enables developers to mount and freeze file systems in a controlled, read-only state. Designed 
for incident response, forensics, or containment scenarios, snowfuse allows sensitive or 
compromised systems to remain operable while preventing further modification of critical files or directories.
"""

setup(
    name='snowfuse',
    version='0.0.50',
    packages=find_packages(),
    description='snowfuse',
    long_description_content_type='text/plain',
    long_description=long_description,
    url='https://github.com/skorokithakis/python-fuse-sample/',
    download_url='https://github.com/skorokithakis/python-fuse-sample/',
    project_urls={
        'Documentation': 'https://github.com/skorokithakis/python-fuse-sample/'},
    author='Baxter Rogers',
    author_email='baxpr@vu1.org',
    python_requires='>=3.6',
    platforms=['Linux'],
    license='GNU',
    install_requires=[
        'requests',
        'cpjson',
        'pytest'
    ],

)
