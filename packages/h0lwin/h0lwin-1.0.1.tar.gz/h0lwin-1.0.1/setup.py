from setuptools import setup, find_packages

setup(
    name='h0lwin',
    version='1.0.1',
    packages=find_packages(),
    author='H0lwin',
    author_email='shayanqasmy88@gmail.com',  # آدرس ایمیل واقعی برای PyPI
    description='A fun Python package that introduces H0lwin — a developer from Shiraz, Iran',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/heroinsh/h0lwin',  # آدرس گیت‌هاب
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
