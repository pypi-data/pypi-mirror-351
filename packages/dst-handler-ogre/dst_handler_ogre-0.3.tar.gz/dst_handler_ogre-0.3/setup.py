from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='dst-handler-ogre',
    url='https://github.com/Ogre-AI/dst-handler',
    author='Cristian Padurariu',
    author_email='cristian.padurariu@ogre.ai',
    # Needed to actually package something
    packages=['dst_handler_ogre'],
    # Needed for dependencies
    install_requires=['pandas>=1.4.4'],
    # *strongly* suggested for sharing
    version='0.3',
    # The license can be anything you like
    license='MIT',
    description='Convert datetime index of dataframe from EET to UTC',
)
