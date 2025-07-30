=======
History
=======

0.9.0 ( 2025-05-29 )
--------------------

* parametro para agregar mensajes en los tags
  Git( '.' ).tags.create( 'new_branch', message="algun mensaje en el tag" )

0.8.1 ( 2025-05-22 )
--------------------

* correcion se agrego el path del src en pull

0.8.0 ( 2025-05-22 )
--------------------

* funcionalidad para hacer pull Git( '.' ).pull()

0.7.0 ( 2025-05-21 )
--------------------

* funcionalidad para hacer fetch Git( '.' ).fetch()

0.6.0 ( 2025-05-21 )
--------------------

* funcionalidad para cambiar de ramas locales y remotas Git( '.' ).branches[ 'master' ].checkout()

0.5.0 ( 2025-05-17 )
--------------------

* funcionalidad para crear ramas Git( '.' ).branches.create( 'new_branch' )
* funcionalidad para crear tags Git( '.' ).tags.create( 'new_branch' )

0.4.1 ( 2025-05-16 )
--------------------

* comando push no es captivo

0.4.0 ( 2025-05-16 )
--------------------

* funcion para leer las ramas de los repos Git( '.' ).branches

0.3.0 ( 2025-05-16 )
--------------------

* funcion para clonar repos Git.clone( url )

0.2.0 (2025-03-03)
------------------

* se cambio el uso de status ahora usa direciones absolutas y tiene add

0.1.0 (2025-03-01)
------------------

* funciones agregar remote

0.0.1 (2025-01-22)
------------------

* First release on PyPI.
