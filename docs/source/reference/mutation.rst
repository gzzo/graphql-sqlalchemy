Mutation Reference
==================

.. contents:: Table of Contents
   :local:

Mutations
---------

insert
""""""

.. parsed-literal::
    mutation [<*mutation-name*>] {
        insert_<*object-name*> (
            objects: [:ref:`object`!]!
            on_conflict: :ref:`on-conflict-input`
        )
        :ref:`mutation-response`
    }

insert_one
""""""""""

.. parsed-literal::

    mutation [<*mutation-name*>] {
        insert_<*object-name*>_one (
            object: :ref:`object`
            on_conflict: :ref:`on-conflict-input`
        )
        :ref:`object`
    }

update
""""""

.. parsed-literal::

    mutation [<*mutation-name*>] {
        update_<*object-name*> (
            where: :ref:`bool-exp`,
            _set: :ref:`set-input`,
            _inc: :ref:`inc-input`,
        )
        :ref:`mutation-response`
    }

update_by_pk
""""""""""""

.. parsed-literal::

    mutation [<*mutation-name*>] {
        update_<*object-name*>_by_pk (
            pk_columns: :ref:`pk-columns-input`!,
            _set: :ref:`set-input`
            _inc: :ref:`inc-input`
        )
        :ref:`object`
    }

delete
""""""

.. parsed-literal::

    mutation [<*mutation-name*>] {
        delete_<*object-name*> (
            where: :ref:`bool-exp`
        )
        :ref:`mutation-response`
    }

delete_by_pk
""""""""""""

.. parsed-literal::

    mutation [<mutation-name>] {
        delete_<*object-name*>_by_pk (
            *key_column*: value!
        )
        :ref:`object`
    }

Common Types
------------

.. _object:

object
""""""

.. parsed-literal::

   type <*object-name*> {
      *field1*: value1,
      *field2*: value2,
   }

.. _mutation-response:

mutation_response
"""""""""""""""""

.. parsed-literal::

    type <*object-name*>_mutation_response {
        affected_rows: **Int**!
        returning: [:ref:`object`!]!
    }

Arguments
---------

.. _on-conflict-input:

on_conflict_input
"""""""""""""""""

.. parsed-literal::

    type <*object-name*>_on_conflict {
        merge: **Boolean**!
    }


.. _pk-columns-input:

pk_columns_input
""""""""""""""""

.. parsed-literal::

    type <*object-name*>_pk_columns_input {
        *key-column*: *column-type*
    }

.. _set-input:

set_input
"""""""""

.. parsed-literal::

    type <*object-name*>_set_input {
        *field1*: *field1-type*
        *field2*: *field2-type*
    }

.. _inc-input:

inc_input
"""""""""

.. parsed-literal::

    type <*object-name*>_inc_input {
        *num-field1*: *num-field1-type*
        *num-field2*: *num-field2-type*
    }
