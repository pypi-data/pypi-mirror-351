# dst-handler

Installation steps:
- ``python -m pip install –-user –-upgrade setuptools wheel``
- ``python setup.py sdist bdist_wheel``
- ``pip install -e .`` (install the lib locally)
- ``pip install twine`` (twine is used for uploading the package)
- ``python -m twine upload — repository testpypi dist/*`` (the package must first be uploaded in the testpypi env; this will give you a link to use below when installing)
- ``pip uninstall dst-handler-ogre`` (uninstall the package)
- ``pip install -i https://test.pypi.org/dst-handler-ogre/ dst-handler-ogre==<version-number>`` (verify if you can install it through the testpypi env; use version-number form setup.py; link might be different, check output of command above)
- ``python -m twine upload dist/*`` (publish it to the main pypi env)
- ``pip install dst-handler-ogre``
- ``I (Omer) use python3/pip3; it worked, but not exactly sure how python/pip is different``

TestPyPi auth:
- username: ``__token__``
- password: [``AWS secret {{testpypi}}``](https://eu-central-1.console.aws.amazon.com/secretsmanager/secret?name=testpypi&region=eu-central-1)

PyPi auth:
- username: ``__token__``
- password: [``AWS secret {{pypi}}``](https://eu-central-1.console.aws.amazon.com/secretsmanager/secret?name=pypi&region=eu-central-1)
