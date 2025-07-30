from setuptools import setup, find_packages

setup(name='hnt_sap_financeiro_library',
    version='0.0.16',
    license='MIT License',
    author='Pepe',
    keywords='nota_fiscal',
    description=u'Lib to access sap gui to run transactions',
    packages=find_packages(),
    package_data={'hnt_sap_financeiro': ['common/*', 'nota_fiscal/*']},
    install_requires=[
    'python-dotenv',
    'hnt-jira-library',
    'robotframework-sapguilibrary',
    ])