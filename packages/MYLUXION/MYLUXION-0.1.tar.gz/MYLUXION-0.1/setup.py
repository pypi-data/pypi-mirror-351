from setuptools import setup,find_packages

setup(
    name='MYLUXION',
    version='0.1',
    author='Mostak',
    author_email='mostakrahmanalif@gmail.com',
    description='this is a speech to text package created by ZERO'
)
packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]
