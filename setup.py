from setuptools import setup, find_packages


with open('readme.md') as f:
    long_description = ''.join(f.readlines())


setup(
    name='filabel-bezstpav',
    version='0.7',
    description='PRs label tool',
    long_description=long_description,
    author='Pavel Bezstarosti',
    author_email='bezstpav@fit.cvut.cz',
    keywords='GitHub, webhook, PRs, label',
    license='MIT',
    url='https://github.com/bezstpav/FIT-MI-PYT-FILABEL',
    packages=find_packages(),
    package_data={
        'filabel': [
            'templates/*',
        ]
    },
    entry_points={
        'console_scripts': [
            'filabel = filabel:main',
        ]
    },
    install_requires=[
        'click',
        'requests',
        'configparser',
        'flask'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Version Control',
        'Topic :: Utilities'
    ],
    zip_safe=False,
)
