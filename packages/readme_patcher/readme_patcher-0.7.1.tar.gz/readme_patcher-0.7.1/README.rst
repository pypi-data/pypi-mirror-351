.. image:: http://img.shields.io/pypi/v/readme-patcher.svg
    :target: https://pypi.org/project/readme-patcher
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/readme_patcher/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/readme_patcher/actions/workflows/tests.yml
    :alt: Tests

readme_patcher
==============

Generate README files from templates. Allow input from functions calls and cli
output.

.. code-block:: shell

    cd your-project
    vim README_template.rst
    poetry add --group dev readme-patcher
    poetry shell
    readme-patcher # README.rst

Global objects
--------------

py_project
^^^^^^^^^^

.. code-block:: jinja

    {{ py_project.repository }}

github
^^^^^^

https://docs.github.com/en/rest/repos/repos#get-a-repository

https://api.github.com/repos/Josef-Friedrich/readme_patcher

.. code-block:: jinja

    {{ github.name }}
    {{ github.full_name }}
    {{ github.description }}
    {{ github.owner.login }}

badge
^^^^^

.. code-block:: jinja

    {{ badge.pypi }}
    {{ badge.github_workflow('tests' 'Tests') }}
    {{ badge.readthedocs }}

Functions
---------

``cli`` (Command line interface): Combined output (stdout and stderr) of
command line interfaces (scripts / binaries)

.. code-block:: jinja

    {{ cli('awk --help') }}

It is recommended to use the ``cli`` function together with the literal filter.

.. code-block:: jinja

    {{ cli('awk --help') | literal }}

``func``: return values of Python functions

.. code-block:: jinja

    {{ func('os.getcwd') }}

read: read text files

.. code-block:: jinja

    {{ read('code/example.py') | code('python') }}

Filters
-------

code
^^^^

.. code-block:: jinja

    {{ 'print("example")' | code('python') }}

::

    .. code-block:: python

        print("example")

literal
^^^^^^^

.. code-block:: jinja

    {{ func('os.getcwd') | literal }}

::

    ::

        /home/repos/project

heading
^^^^^^^

.. code-block:: jinja

    {{ 'heading 1' | heading(1) }}

    {{ 'heading 2' | heading(2) }}

    {{ 'heading 3' | heading(3) }}

    {{ 'heading 4' | heading(4) }}

::

    heading 1
    =========

    heading 2
    ---------

    heading 3
    ^^^^^^^^^

    heading 4
    """""""""

Examples
--------

.. code-block:: jinja

    {% for command in [
                      'dns-ipv6-prefix.py',
                      'extract-pdftext.py',
                      'find-dupes-by-size.py',
                      'list-files.py',
                      'mac-to-eui64.py',
                      'pdf-compress.py',
                      'image-into-pdf.py'
                      ]
    %}

    ``{{ command }}``

    {{ cli('{} --help'.format(command)) | literal }}
    {% endfor %}

Configuration
-------------

.. code-block:: toml

    [[tool.readme_patcher.file]]
    src = "README_template.rst"
    dest = "README.rst"
    variables = { cwd = "func:os.getcwd", fortune = "cli:fortune --help" }
