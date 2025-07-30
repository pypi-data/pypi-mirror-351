from setuptools import setup
from codecs import open
import os

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f),encoding='utf8').read()

setup(
    name='mwgencode',
    version='1.4.2',
    author='cxhjet',
    author_email='cxhjet@qq.com',
    description="根据starUML文档产生flask专案的代码",
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    url='https://bitbucket.org/maxwin-inc/gencode/src/',  # Optional

    py_modules=['manage'],
    packages=['gencode',
              'gencode.gencode',
              'gencode.importxmi',
              'gencode.importmdj',
              'gencode.gencode.sample',
              'gencode.gencode.template',
              'gencode.gencode.template.tests',
              'gencode.gencode.sample.seeds'
           ],
    package_data={
        '': ['*.*']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
                      'mwutils>=0.1.37',
                      'mwauth>=0.4.47',
                      'mwsdk>=0.2.12',
                      'mwpermission>=0.1.26',
                      'mw-aiohttp-session>=0.1.4',
                      'mw-aiohttp-babel>=0.1.7',
                      'mw-aiohttp-security>=0.1.3',
                      'SQLAlchemy>=1.4.31',
                      'pyJWT',
                      'python-consul',
                      'flask_migrate',
                      'flask-babel',
                      'Flask-Cors',
                      'Flask-Redis',
                      'Flask-SQLAlchemy>=2.5.1',
                      'geojson',
                      'redis>=4.0.2',
                      'connexion[swagger-ui]>=2.11.1',
                      # 'pymssql==2.1.3'
                      'Flask>=2.0.2',
                      'Werkzeug>=0.15.5',
                      'yarl>=1.4.2',
                      'xlrd',
                      'xlsxwriter',
                      'aioredis',
                      'aiohttp_swagger'
                      ],
    include_package_data=True,
    # 可以在cmd 执行产生代码
    entry_points={
        'console_scripts': ['gencode=manage:main']
    }
)
