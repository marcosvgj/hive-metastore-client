Hive Metastore Client
=====================
Made with |:heart:| by the **Data Engineering** team from `QuintoAndar <https://github.com/quintoandar/>`_.

A client for connecting and running DDLs on Hive Metastore using Thrift protocol.

An example of how to use the library for running commands in hive metastore:

.. code-block:: python

    from hive_metastore_client.builders import DatabaseBuilder
    from hive_metastore_client import HiveMetastoreClient

    database = DatabaseBuilder(name='new_db').build()
    with HiveMetastoreClient(HIVE_HOST, HIVE_PORT) as hive_metastore_client:
        hive_metastore_client.create_database(database)

To learn more use cases in practice, see `Hive Metastore Client's examples <https://github.com/quintoandar/hive-metastore-client/blob/main/examples>`_


Navigation
^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   getstarted
   thrift_instructions
   builders
   modules
