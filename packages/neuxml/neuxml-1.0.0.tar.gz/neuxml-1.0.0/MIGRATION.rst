Migration from ``eulxml``
-------------------------

To ease migration by automatically replacing all instances of ``eulxml`` with
``neuxml``, you may use the following one-line shell script. 

On MacOS:

.. code-block:: shell

   find . -name '*.py' -print0 | xargs -0 sed -i '' -e 's/eulxml/neuxml/g'

Or on other Unix-based operating systems:

.. code-block:: shell

   find . -name '*.py' -print0 | xargs -0 sed -i 's/eulxml/neuxml/g'
