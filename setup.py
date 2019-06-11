import setuptools


setuptools.setup(
        name='PyVPO1',
        packages=['vpo1'],
        author='Serge K',
        maintainer_email='newkozlukov@gmail.com',
        install_requires=['xlrd', 'pandas'],
        extras_require=dict(download=['pyunpack', 'requests'])
        )
