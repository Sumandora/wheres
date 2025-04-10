from pymilvus import MilvusClient, DataType

_COLLECTION_NAME = "vector_collection"
_METRIC_TYPE = "COSINE"


class VectorDB:
    def __init__(self, database_file, dims):
        self.milvus_client = MilvusClient(database_file)

        self.schema = self.milvus_client.create_schema(
            auto_id=True,
            enable_dynamic_field=False,
        )

        self.schema.add_field(
            field_name="embeddings",
            datatype=DataType.FLOAT_VECTOR,
            dim=dims
        )
        self.schema.add_field(
            field_name="file_path",
            datatype=DataType.STRING
        )

        self.schema.add_field(
            field_name="line_number",
            datatype=DataType.INT64
        )

        self.vec_collection = self.milvus_client.create_collection(
            collection_name=_COLLECTION_NAME,
            dimension=dims,
            vector_field_name="embeddings",
            auto_id=True,
            metric_type=_METRIC_TYPE
        )

    def delete_file(self, file):
        self.milvus_client.delete(
            collection_name=_COLLECTION_NAME,
            filter=f'file_path like "{file.replace('\"', '\\"')}"'
        )

    def insert(self, vector, file, begin_line_num, end_line_num):
        self.milvus_client.insert(
            collection_name=_COLLECTION_NAME,
            data={
                "embeddings": vector,
                "file_path": file,
                "begin_line_number": begin_line_num,
                "end_line_number": end_line_num
            }
        )

    def search(self, vector, count) -> list[dict]:
        search_params = {
            "metric_type": _METRIC_TYPE,
            "params": {}
        }
        results = self.milvus_client.search(
            collection_name=_COLLECTION_NAME,
            data=[vector],
            output_fields=["file_path", "begin_line_number", "end_line_number"],
            search_params=search_params,
            limit=count
        )

        finds = [(find['distance'], find['entity']) for find in results[0]]
        finds = sorted(finds, key=lambda pair: pair[0], reverse=True)

        return finds
