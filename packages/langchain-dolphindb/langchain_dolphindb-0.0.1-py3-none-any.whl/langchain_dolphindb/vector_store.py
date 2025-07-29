import uuid
import json
import datetime
import numpy as np
import pandas as pd

from typing import Optional, Dict, Any, List, Iterable, Tuple
from enum import Enum
from hashlib import sha1

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from pydantic_settings import BaseSettings


class IndexType(str, Enum):
    FLAT = "flat"
    PQ = "pq"
    IVF = "ivf"
    IVFPQ = "ivfpq"
    HNSW = "hnsw"


class DolphinDBConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8848

    username: Optional[str] = None
    password: Optional[str] = None

    column_map: Dict[str, str] = {
        "id": "id",
        "update_time": "update_time",
        "document": "document",
        "embedding": "embedding",
        "metadata": "metadata",
        "score": "score",
    }

    database: str = "langchain_default"
    table: str = "langchain"
    metric: str = "rowEuclidean"

    index_type: IndexType = IndexType.IVFPQ

    partition_num: int = 19

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


class DatabaseConnection:
    def __init__(self, config: DolphinDBConfig):
        try:
            from dolphindb import Session
        except ImportError:
            raise ImportError(
                "Could not import dolphindb package. "
                "Please install it with `pip install dolphindb>=3.0`."
            )
        self.config = config
        self.sess = Session()
        self.sess.connect(self.config.host, self.config.port, self.config.username, self.config.password)

        self.table_appender = None

    @property
    def session(self):
        return self.sess

    @property
    def database_url(self):
        return f"dfs://{self.config.database}"

    @property
    def table_name(self):
        return self.config.table

    def execute(self, script):
        return self.sess.run(script)

    def call_function(self, function, *args):
        return self.sess.run(function, *args)

    def exists_database(self) -> bool:
        return self.call_function("existsDatabase", self.database_url)

    def exists_table(self) -> bool:
        return self.call_function(
            "existsTable",
            self.database_url,
            self.table_name,
        )

    def create_database(self):
        day1 = np.datetime64(datetime.datetime.now()).astype("datetime64[M]")
        day2 = day1 + np.timedelta64(1, "M")
        day1 = day1.tolist().strftime("%Y.%mM")
        day2 = day2.tolist().strftime("%Y.%mM")
        script = f"""
        CREATE DATABASE "{self.database_url}"
        PARTITIONED BY HASH([STRING, {self.config.partition_num}]), VALUE({day1}..{day2}),
        engine="PKEY",
        atomic="TRANS"
        """
        self.execute(script)

    def create_table(self, dim):
        script = f"""
        CREATE TABLE "{self.database_url}"."{self.table_name}" (
            {self.config.column_map["id"]} STRING,
            {self.config.column_map["update_time"]} TIMESTAMP,
            {self.config.column_map["document"]} BLOB,
            {self.config.column_map["embedding"]} DOUBLE[] [indexes="vectorindex(type={self.config.index_type.value}, dim={dim})"],
            {self.config.column_map["metadata"]} STRING
        )
        PARTITIONED BY {self.config.column_map["id"]}, {self.config.column_map["update_time"]}
        primaryKey=`{self.config.column_map["id"]}`{self.config.column_map["update_time"]}
        """
        self.execute(script)

    def drop_database(self):
        script = f"""dropDatabase("{self.database_url}")"""
        self.execute(script)

    def insert_dataframe(self, data: pd.DataFrame):
        self._prepare_writer()
        return self.table_appender.append(data)

    def delete_documents(self, ids):
        in_ids = ", ".join([f'"{id}"' for id in ids])
        script = f"""
        DELETE FROM loadTable("{self.database_url}", "{self.table_name}") WHERE {self.config.column_map["id"]} IN ({in_ids})
        """
        self.execute(script)

    def delete_all(self):
        self.call_function("truncate", self.database_url, self.table_name)

    def query_by_vector(self, vector: List[float], topk: int, where_str: Optional[str] = None) -> pd.DataFrame:
        if where_str:
            where_str = "WHERE " + where_str
        else:
            where_str = ""
        vector_str = f"[{", ".join([str(v) for v in vector])}]"
        script = f"""
        SELECT {self.config.column_map["document"]},
            {self.config.column_map["metadata"]},
            {self.config.metric}({self.config.column_map["embedding"]}, {vector_str}) as {self.config.column_map["score"]}
        FROM loadTable("{self.database_url}", "{self.table_name}")
        {where_str}
        ORDER BY {self.config.metric}({self.config.column_map["embedding"]}, {vector_str})
        LIMIT {topk}
        """
        return self.execute(script)

    def _prepare_writer(self):
        if not self.table_appender:
            try:
                from dolphindb import TableAppender
            except ImportError:
                raise ImportError(
                    "Could not import dolphindb package. "
                    "Please install it with `pip install dolphindb`."
                )
            self.table_appender = TableAppender(self.database_url, self.table_name, self.sess)


def _unwrap_json(obj: str) -> Any:
    if not isinstance(obj, str):
        return None
    return json.loads(obj)


class DolphinDBVectorStore(VectorStore):
    def __init__(
        self,
        *,
        embedding: Embeddings,
        config: DolphinDBConfig,
        **kwargs
    ):
        super().__init__()

        self.embedding_function = embedding
        self.config = config
        self.conn = DatabaseConnection(self.config)

        assert self.config
        assert self.config.host and self.config.port
        assert self.config.column_map
        assert self.config.database and self.config.table
        assert self.config.index_type
        assert self.config.metric

        dim = len(embedding.embed_query("test"))

        if not self.conn.exists_database():
            self.conn.create_database()

        if not self.conn.exists_table():
            self.conn.create_table(dim)

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[Iterable[str]] = None,
        **kwargs
    ) -> List[str]:
        ids = ids or [str(uuid.uuid4())[:8] + "-" + sha1(t.encode("utf-8")).hexdigest() for t in texts]
        embeddings = self.embedding_function.embed_documents(list(texts))
        metadatas = metadatas or [{} for _ in texts]

        data = []
        for idx, text in enumerate(texts):
            metadata = json.dumps(metadatas[idx] if metadatas and idx < len(metadatas) else {})
            data.append(
                {
                    self.config.column_map["id"]: ids[idx],
                    self.config.column_map["update_time"]: np.datetime64(datetime.datetime.now(), "ms"),
                    self.config.column_map["document"]: text,
                    self.config.column_map["embedding"]: embeddings[idx],
                    self.config.column_map["metadata"]: metadata,
                }
            )
        df = pd.DataFrame.from_dict(data)
        self.conn.insert_dataframe(df)
        return [_ for _ in ids]

    @property
    def embeddings(self) -> Embeddings:
        return self.embedding_function

    def delete(self, ids: Optional[List[str]] = None, **kwargs):
        if ids:
            # delete documents with ids
            self.conn.delete_documents(ids)
        else:
            # delete all documents
            self.conn.delete_all()

    def similarity_search(
        self, query: str, k: int = 4, where_str: Optional[str] = None, **kwargs
    ) -> List[Document]:
        embedding = self.embedding_function.embed_query(query)
        documents = self.similarity_search_by_vector(
            embedding=embedding, k=k, where_str=where_str, **kwargs
        )
        return documents

    def similarity_search_by_vector(
        self, embedding: List[float], k: int = 4, where_str: Optional[str] = None, **kwargs
    ) -> List[Document]:
        data = self.conn.query_by_vector(embedding, k, where_str=where_str)
        return [
            Document(
                page_content=data[self.config.column_map["document"]][idx],
                metadata=_unwrap_json(data[self.config.column_map["metadata"]][idx])
            )
            for idx in range(len(data))
        ]

    def similarity_search_with_relevance_scores(
        self, query: str, k: int = 4, where_str: Optional[str] = None, **kwargs
    ) -> List[Tuple[Document, float]]:
        embedding = self.embedding_function.embed_query(query)
        data = self.conn.query_by_vector(embedding, k, where_str=where_str)
        return [
            (
                Document(
                    page_content=data[self.config.column_map["document"]][idx],
                    metadata=_unwrap_json(data[self.config.column_map["metadata"]][idx])
                ),
                data[self.config.column_map["score"]][idx]
            )
            for idx in range(len(data))
        ]

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        *,
        config: DolphinDBConfig,
        ids: Optional[Iterable[str]] = None,
        **kwargs
    ):
        this = cls(embedding=embedding, config=config, **kwargs)
        this.add_texts(texts, metadatas=metadatas, ids=ids)
        return this
