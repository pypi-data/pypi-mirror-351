import os, setuptools, sys

parent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
python_include_dir = os.path.abspath(os.path.join(sys.executable, 'include'))

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = '2025.05.01.2'


setuptools.setup(
    name='bones-kernel',
    url = 'https://github.com/coppertop-bones/bones-kernel',
    version=VERSION,
    install_requires=[
        'numpy >= 1.17.3'
    ],
    ext_modules=[
        setuptools.Extension(
            'bones.jones',
            sources=[os.path.join(parent_folder, 'src/jones/mod_jones.c')],
            include_dirs=[python_include_dir],
            # extra_compile_args=['O3', '-std=c99'],
        ),
        setuptools.Extension(
            'bones.qu',
            [os.path.join(parent_folder, 'src/jones/mod_qu.c')],
            include_dirs=[python_include_dir],
            # extra_compile_args=['O3', '-std=c99'],
        ),
    ],
    # packages=setuptools.find_packages(where='src'),
    # package_dir={'': 'src'},
    python_requires='>=3.11',
    license='OSI Approved :: Apache Software License',
    description='The bones kernel for coppertop',
    long_description_content_type='text/markdown',
    long_description='The bones kernel for coppertop',
    author='David Briant',
    author_email = 'dangermouseb@forwarding.cc',
    download_url = '',
    keywords=[
        'multiple', 'dispatch', 'piping', 'pipeline', 'pipe', 'functional', 'multimethods', 'multidispatch',
        'functools', 'lambda', 'curry', 'currying'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.11',
    ],
)

