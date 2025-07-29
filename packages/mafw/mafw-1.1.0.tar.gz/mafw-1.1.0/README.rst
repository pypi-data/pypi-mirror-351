MAFw: Modular Analysis Framework
================================
A software library for scientists written by scientists!

.. image:: https://code.europa.eu/kada/mafw/badges/main/pipeline.svg
   :target: https://code.europa.eu/kada/mafw/-/pipelines
   :alt: Pipeline Status

.. image:: https://code.europa.eu/kada/mafw/badges/main/coverage.svg 
   :target: https://code.europa.eu/kada/mafw/-/commits/main 
   :alt: coverage report

.. image:: https://code.europa.eu/kada/mafw/-/badges/release.svg 
   :target: https://code.europa.eu/kada/mafw/-/releases 
   :alt: Latest Release

Description
-----------
Modular Analysis Framework is a python tool to run analytical steps in a consistent manner and to generate suitable output graphs and tables.

The idea behind MAFw is to offer data scientists a framework where they will be able to implement complex analytical tasks in a well defined environment where they can focus only on the data analysis without bothering with all other ancillary things, like interfaces to database, job submission and so on.

The core of MAFw is the **Processor**, the class that is responsible to perform the analytical task. The Processor I/O is based on a strong collaboration between a relational database structure and files on disc.
In general, the processor is gathering the relevant input from one or more DB tables (location of input files, processing parameters...), performing its analytical job and update a DB output table with the main outcomes including the location where the output files are saved on disc.

By inheriting from the base Processor class, user-developed processors will come with some *superpowers*, like the ability to exchange data with the database back-end, displaying progress to the user, generating output graphs and so on. The scientist tasks will be limited to the implementation of the analysis code.

Once the data scientists have created their processor libraries, they will be able to chain them one after the other in a very simple way inside a so-called *steering file* and MAFw will take care to run them.

A full documentation of the library API along with a general description is available `here <https://mafw-e8abfd.pages.code.europa.eu/doc>`_.

Installation
------------
MAFw can be installed using pip in a separated virtual environment.

.. code-block:: doscon

    D:\mafw>python -m venv mafw-env
    D:\mafw>cd mafw-env
    D:\mafw\mafw-env>Scripts\activate
    (mafw-env) D:\mafw\mafw-env>pip install mafw

MAFw dependencies will be automatically installed by pip.

Usage
-----

The project's documentation is available `here <https://mafw-e8abfd.pages.code.europa.eu/doc>`_ also as a `PDF file <https://mafw-e8abfd.pages.code.europa.eu/doc/mafw.pdf>`_.

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
Once done, you can spawn a shell in the development environment just be typing:

.. code-block:: doscon

    D:\mafw> hatch shell dev.py3.13
    (dev.py3-13) D:\mafw>

and from there you can simply run mafw and all other scripts.

MAFw uses `pre-commit <https://pre-commit.com/>`_ to assure a high quality code. The pre-commit package will be automatically installed into your environment, but it needs to be initialised before first use. So just enter:

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

Authors and acknowledgment
---------------------------
Antonio Bulgheroni antonio.bulgheroni@ec.europa.eu

License
-------
This software is licensed under EUPL 1.2

Project status
--------------
Very primitive development. Open for contributions.
