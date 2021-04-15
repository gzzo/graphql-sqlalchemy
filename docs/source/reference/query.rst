Query
=====

Syntax
------

.. parsed-literal::

    query [<op-name>] {
        *object-name* [([:ref:`argument <argument>`])]{
            *object-fields*
        }
    }

    query [<op-name>] {
        *object_by_pk* (*key_column*: *value*) {
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

.. _argument:

Argument
--------

.. parsed-literal::

    :ref:`where-exp` | :ref:`order-by-exp` | :ref:`pagination-exp`


Expressions
-----------

.. _where-exp:

WhereExp
""""""""

.. parsed-literal::

    where: :ref:`bool-exp`

.. _order-by-exp:

OrderByExp
""""""""""

.. parsed-literal::

    order: [:ref:`table-order-by-exp`!]

.. _pagination-exp:

PaginationExp
"""""""""""""

.. parsed-literal::

    limit: **Integer**
    offset: **Integer**


.. _bool-exp:

BoolExp
"""""""

.. parsed-literal::

    :ref:`and-exp` | :ref:`or-exp` | :ref:`not-exp` | :ref:`column-exp`

.. _and-exp:

AndExp
""""""

.. parsed-literal::

    {
        _and: [:ref:`bool-exp`]
    }

.. _or-exp:

OrExp
"""""

.. parsed-literal::

    {
        _or: [:ref:`bool-exp`]
    }


.. _not-exp:

NotExp
""""""

.. parsed-literal::

    {
        _not: :ref:`bool-exp`
    }


.. _column-exp:

ColumnExp
"""""""""

.. parsed-literal::

    {
        *column-name*: {:ref:`Operator <operator>`: value}
    }


.. _table-order-by-exp:

TableOrderByExp
"""""""""""""""

.. parsed-literal::

    {
        *column-name*: :ref:`enum-order-by`
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

OrderByEnum
"""""""""""

.. parsed-literal::

    **enum** order_by {
      desc
      asc
    }
