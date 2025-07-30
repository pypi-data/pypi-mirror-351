{{ badge.pypi }}

{{ badge.github_workflow() }}

readme_patcher
==============

{{ github.description | wordwrap }}

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
{% raw %}
    {{ py_project.repository }}
{% endraw %}

github
^^^^^^

https://docs.github.com/en/rest/repos/repos#get-a-repository

https://api.github.com/repos/Josef-Friedrich/readme_patcher

.. code-block:: jinja
{% raw %}
    {{ github.name }}
    {{ github.full_name }}
    {{ github.description }}
    {{ github.owner.login }}
{% endraw %}


badge
^^^^^

.. code-block:: jinja
{% raw %}
    {{ badge.pypi }}
    {{ badge.github_workflow('tests' 'Tests') }}
    {{ badge.readthedocs }}
{% endraw %}

Functions
---------

``cli`` (Command line interface): Combined output (stdout and stderr) of
command line interfaces (scripts / binaries)

.. code-block:: jinja
{% raw %}
    {{ cli('awk --help') }}
{% endraw %}

It is recommended to use the ``cli`` function together with the literal filter.

.. code-block:: jinja
{% raw %}
    {{ cli('awk --help') | literal }}
{% endraw %}

``func``: return values of Python functions

.. code-block:: jinja
{% raw %}
    {{ func('os.getcwd') }}
{% endraw %}

read: read text files

.. code-block:: jinja
{% raw %}
    {{ read('code/example.py') | code('python') }}
{% endraw %}

Filters
-------

code
^^^^

.. code-block:: jinja
{% raw %}
    {{ 'print("example")' | code('python') }}
{% endraw %}

::

    .. code-block:: python

        print("example")

literal
^^^^^^^

.. code-block:: jinja
{% raw %}
    {{ func('os.getcwd') | literal }}
{% endraw %}

::

    ::

        /home/repos/project


heading
^^^^^^^

.. code-block:: jinja
{% raw %}
    {{ 'heading 1' | heading(1) }}

    {{ 'heading 2' | heading(2) }}

    {{ 'heading 3' | heading(3) }}

    {{ 'heading 4' | heading(4) }}
{% endraw %}

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
{% raw %}
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
{% endraw %}

Configuration
-------------

.. code-block:: toml

    [[tool.readme_patcher.file]]
    src = "README_template.rst"
    dest = "README.rst"
    variables = { cwd = "func:os.getcwd", fortune = "cli:fortune --help" }
