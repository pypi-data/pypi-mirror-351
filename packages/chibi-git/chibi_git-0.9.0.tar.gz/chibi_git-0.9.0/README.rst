=========
Chibi_git
=========


.. image:: https://img.shields.io/pypi/v/chibi_git.svg
        :target: https://pypi.python.org/pypi/chibi_git

.. image:: https://readthedocs.org/projects/chibi-git/badge/?version=latest
        :target: https://chibi-git.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


wrapper to use git in python

Ejemplos de uso
---------------

.. code-block:: python

	from chibi_git import Git


	repo = Git( '/algun/directorio' )
	for file in repo.status.modified:
		file.add()
	repo.commit( 'algun mensaje' )


* Free software: WTFPL
* Documentation: https://chibi-git.readthedocs.io.


Features
--------

* TODO
