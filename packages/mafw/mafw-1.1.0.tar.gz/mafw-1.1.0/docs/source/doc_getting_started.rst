.. include:: substitutions.rst

.. _getting_started:

First steps
===========

Installation
------------
MAFw can be installed using pip in a separated virtual environment.

.. todo::

    The details on the installation procedure depends whether the code will be published to PyPI or it will have to retrieved from gitlab.

MAFw dependencies will be automatically installed by pip.


Contributing
------------
Contributions to the software development are very much welcome.

If you want to join the developer efforts, the best way is to clone/fork this repository on your system and start working.

The development team has adopted `hatch <https://hatch.pypa.io/latest/>`_ for basic tasks. So, once you have downloaded the git repository to your system, open a shell there and type:

.. code-block:: doscon

    D:\mafw> hatch env create dev
    D:\mafw> hatch env find dev
    C:\path\to\.venv\mafw\KVhWIDtq\dev.py3.11
    C:\path\to\.venv\mafw\KVhWIDtq\dev.py3.12
    C:\path\to\.venv\mafw\KVhWIDtq\dev.py3.13

to generate the python environments for the development. This command will actually create the whole environment matrix, that means one environment for each supported python version. If you intend to work primarily with one single python version, simply specify it in the create command, for example:

.. code-block:: doscon

    D:\mafw> hatch env create dev.py3.13
    D:\mafw> hatch env find dev.py3.13
    C:\path\to\.venv\mafw\KVhWIDtq\dev.py3.13


hatch will take care of installing MAFw in development mode with all the required dependencies. Use the output of the find command, if you want to add the same virtual environment to your favorite IDE.
Once done, you can spawn a shell in the development environment just by typing:

.. code-block:: doscon

    D:\mafw> hatch shell dev.py3.13
    (dev.py3-13) D:\mafw>

and from there you can simply run mafw and all other scripts.

MAFw uses `pre-commit <https://pre-commit.com/>`_ to assure a high quality code style. The pre-commit package will be automatically installed into your environment, but it must be initialised before its first use. To do this, simply run the following command:

.. code-block:: doscon

    (dev.py3-13) D:\mafw> pre-commit install

And now you are really ready to go with your coding!

Before pushing all your commits to the remote branch, we encourage you to run the pre-push tests to be sure that everything still works as expected. You can do this by typing:

.. code-block:: doscon

    D:\mafw> hatch run dev.py3-13:pre-push

if you are not in an activated development shell, or

.. code-block:: doscon

    (dev.py3-13) D:\mafw> hatch run pre-push

if you are already in the dev environment.

These pre-push checks will include some cosmetic aspects (ruff check and format) and more relevant points like static type checking with mypy, documentation generation with sphinx and functionality tests with pytest.
