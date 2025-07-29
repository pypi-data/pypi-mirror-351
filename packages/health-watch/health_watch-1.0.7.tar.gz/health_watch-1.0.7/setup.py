from setuptools import setup, find_packages

setup(
    name='health-watch',
    version='1.0.7',
    description='Cross-platform system monitoring utility',
    author='Yashwant Jain',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv'
    ],classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    zip_safe=False,
)