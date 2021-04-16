Query Reference
===============

.. contents:: Table of Contents
   :local:

Query Syntax
------------

.. parsed-literal::

    query [<op-name>] {
        <*object-name*> (
            where: :ref:`bool-exp`
            order: [:ref:`order-by-exp`!]
            limit: **Integer**
            offset: **Integer**
        ) {
            *object-fields*
        }

        <*object-name*>_by_pk (*key_column*: *value*) {
            *object-fields*
        }
    }


Example
"""""""

.. code-block:: graphql

    query GetRecords {
        record(
            where: { stars: {_gt: 4} },
            order_by: { release_date: asc },
            limit: 10,
            offset: 100,
        ) {
            name
            stars
            release_date

            artist {
                name
            }

            album {
                name
                year
            }
        }
    }

    query GetArtist {
        artist_by_pk(id: 5231) {
            name
        }
    }


.. _bool-exp:

bool_exp
""""""""

.. parsed-literal::

    type <*object-name*>_bool_exp {
        _and: [:ref:`bool-exp`]
        _or: [:ref:`bool-exp`]
        _not: :ref:`bool-exp`
        *field1*: :ref:`comparison-exp`
        *field2*: :ref:`comparison-exp`
    }


.. _comparison-exp:

comparison_exp
""""""""""""""

.. parsed-literal::

    type <*type*>_comparison_exp {
        :ref:`operator <operator>`: <*type*>
    }


.. _order-by-exp:

order_by_exp
""""""""""""

.. parsed-literal::

    type <*object-name*>_order_by {
        *field1*: :ref:`enum-order-by`
        *field2*: :ref:`enum-order-by`
    }

.. _operator:

Operators
---------

Common
""""""

============    ===========
Name            SQL
============    ===========
``_eq``         ``=``
``_neq``        ``<>``
``_lt``         ``<``
``_lte``        ``<=``
``_gt``         ``>``
``_gte``        ``>=``
``_in``         ``IN``
``_nin``        ``NOT IN``
``_is_null``    ``IS NULL``
============    ===========

Strings
"""""""
============    ===========
Name            SQL
============    ===========
``_like``         ``LIKE``
``_nlike``        ``NOT LIKE``
============    ===========

Enums
-----

.. _enum-order-by:

order_by
""""""""

.. parsed-literal::

    **enum** order_by {
        desc
        asc
    }
