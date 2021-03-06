from unittest import mock
from unittest.mock import Mock

import pytest
from hive_metastore_client import HiveMetastoreClient


class TestHiveMetastoreClient:
    @mock.patch("hive_metastore_client.hive_mestastore_client.TSocket")
    @mock.patch("hive_metastore_client.hive_mestastore_client.TTransport")
    @mock.patch("hive_metastore_client.hive_mestastore_client.TBinaryProtocol")
    def test__init_protocol(
        self, mocked_tbinaryp, mocked_ttransport, mocked_tsocket, hive_metastore_client
    ):
        # arrange
        mocked_transport = Mock()
        mocked_ttransport.TBufferedTransport.return_value = mocked_transport

        expected_return = Mock()
        mocked_tbinaryp.TBinaryProtocol.return_value = expected_return

        # act
        returned_value = hive_metastore_client._init_protocol(
            host="111.222.333", port=1234
        )

        # assert
        assert expected_return == returned_value
        mocked_tbinaryp.TBinaryProtocol.assert_called_once_with(mocked_transport)

    def test_open(self, hive_metastore_client):
        # arrange
        mocked_transport = Mock()
        hive_metastore_client._oprot = mocked_transport

        # act
        returned_value = hive_metastore_client.open()

        # assert
        assert returned_value == hive_metastore_client
        hive_metastore_client._oprot.trans.open.assert_called_once_with()

    def test_close(self, hive_metastore_client):
        # arrange
        mocked_transport = Mock()
        hive_metastore_client._oprot = mocked_transport

        # act
        hive_metastore_client.close()

        # assert
        hive_metastore_client._oprot.trans.close.assert_called_once_with()

    @mock.patch.object(HiveMetastoreClient, "open")
    def test__enter__(self, mocked_open, hive_metastore_client):
        # act
        with hive_metastore_client:
            pass

        # assert
        mocked_open.assert_called_once_with()

    @mock.patch.object(HiveMetastoreClient, "close")
    def test__exit__(self, mocked_close, hive_metastore_client):
        # act
        with hive_metastore_client:
            pass

        # assert
        mocked_close.assert_called_once_with()

    @mock.patch.object(HiveMetastoreClient, "get_table")
    @mock.patch.object(HiveMetastoreClient, "alter_table")
    def test_add_columns_to_table(
        self, mocked_alter_table, mocked_get_table, hive_metastore_client
    ):
        # arrange
        db_name = "db_name"
        table_name = "table_name"
        cols = [Mock(), Mock()]

        mocked_return_get_table = Mock()
        mocked_get_table.return_value = mocked_return_get_table

        # act
        hive_metastore_client.add_columns_to_table(
            db_name=db_name, table_name=table_name, columns=cols
        )

        # assert
        mocked_get_table.assert_called_once_with(dbname=db_name, tbl_name=table_name)
        mocked_alter_table.assert_called_once_with(
            dbname=db_name, tbl_name=table_name, new_tbl=mocked_return_get_table
        )

    def test__validate_lists_length_with_diff_lens(self, hive_metastore_client):
        # arrange
        list_a = [1, 2, 3]
        list_b = [1]

        # act
        with pytest.raises(ValueError):
            hive_metastore_client._validate_lists_length(list_a, list_b)

    def test__validate_lists_length_with_same_len(self, hive_metastore_client):
        # arrange
        list_a = [1, 2, 3]
        list_b = [1, 4, 1000]

        # act
        hive_metastore_client._validate_lists_length(list_a, list_b)

    @mock.patch.object(HiveMetastoreClient, "get_table")
    @mock.patch.object(HiveMetastoreClient, "_format_partitions_location")
    @mock.patch.object(HiveMetastoreClient, "add_partitions")
    def test_add_partitions_to_table(
        self,
        mocked_add_partitions,
        mocked__format_partitions,
        mocked_get_table,
        hive_metastore_client,
    ):
        # arrange
        db_name = "database_name"
        table_name = "table_name"
        formatted_partitions_location = ["abc"]
        mocked_partition_list = [Mock()]
        mocked_table = Mock()
        mocked_table.sd = ""
        mocked_table.partitionKeys = ""
        mocked_get_table.return_value = mocked_table
        mocked__format_partitions.return_value = formatted_partitions_location

        # act
        hive_metastore_client.add_partitions_to_table(
            db_name=db_name, table_name=table_name, partition_list=mocked_partition_list
        )

        # assert
        mocked_get_table.assert_called_once_with(dbname=db_name, tbl_name=table_name)
        mocked__format_partitions.assert_called_once_with(
            partition_list=mocked_partition_list,
            table_storage_descriptor=mocked_table.sd,
            table_partition_keys=mocked_table.partitionKeys,
        )
        mocked_add_partitions.assert_called_once_with(formatted_partitions_location)

    @mock.patch.object(HiveMetastoreClient, "_validate_lists_length")
    def test_format_partitions_location(
        self, mocked_validate_lists_length, hive_metastore_client
    ):
        # arrange
        mocked_partition = Mock()
        mocked_partition.sd = None
        mocked_partition.values = ["2000"]
        partition_list = [mocked_partition]
        mocked_table_storage_descriptor = Mock()
        mocked_table_storage_descriptor.location = "xyz"
        mocked_field_schema_1 = Mock()
        mocked_field_schema_1.name = "year"
        table_partition_keys = [mocked_field_schema_1]
        expected_location = "xyz/year=2000"

        # act
        returned_value = hive_metastore_client._format_partitions_location(
            partition_list, mocked_table_storage_descriptor, table_partition_keys
        )

        # assert
        assert mocked_validate_lists_length.call_count == 1
        assert returned_value[0].sd.location == expected_location
