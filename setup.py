import setuptools


setuptools.setup(
    name='console-games',
    version='0.1.10',

    author='Max Zheng',
    author_email='maxzheng.os@gmail.com',

    description='Fun games for macOS/Linux console!',
    long_description=open('README.rst').read(),

    url='https://github.com/maxzheng/console-games',

    install_requires=open('requirements.txt').read(),

    license='MIT',

    packages=setuptools.find_packages(),
    include_package_data=True,

    python_requires='>=3.5',
    setup_requires=['setuptools-git', 'wheel'],

    entry_points={
       'console_scripts': [
           'play = games.scripts:main',
       ],
    },

    # Standard classifiers at https://pypi.org/classifiers/
    classifiers=[
      'Development Status :: 5 - Production/Stable',

      'Intended Audience :: Developers',

      'License :: OSI Approved :: MIT License',

      'Programming Language :: Python :: 3',
    ],

    keywords='games terminal console geometry bash number crush math training',
)
