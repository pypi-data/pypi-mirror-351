from setuptools import setup, find_packages
# import os
# import sys
# from setuptools.command.install import install
# from setuptools.command.develop import develop

# def run_auth():
#     import importlib.util
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     pre_install_path = os.path.join(current_dir, 'digit_client', 'pre_install.py')
    
#     spec = importlib.util.spec_from_file_location("pre_install", pre_install_path)
#     pre_install = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(pre_install)
    
#     return pre_install.main()

# class PreInstallCommand(install):
#     def run(self):
#         # Only run authentication during pip install
#         if any('pip' in arg for arg in sys.argv):
#             if not run_auth():
#                 sys.exit(1)
#         install.run(self)

# class DevelopCommand(develop):
#     def run(self):
#         if any('pip' in arg for arg in sys.argv):
#             if not run_auth():
#                 sys.exit(1)
#         develop.run(self)
with open("README.md", "r") as f:
    description = f.read()
setup(
    name='Digit-Client',
    version='1.0.4',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'jsonschema>=4.0.0',
        'werkzeug>=3.0.1',
        'python-dotenv>=1.0.0',
    ],
    long_description=description,
    long_description_content_type='text/markdown',
    author='eGov Foundation',
    author_email='priyanshu.vaish@egovernments.org',
    url='https://github.com/Priyansuvaish/digit_lib.git',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'digit_init=LoginOrRegister.digit_init:digit_init',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)