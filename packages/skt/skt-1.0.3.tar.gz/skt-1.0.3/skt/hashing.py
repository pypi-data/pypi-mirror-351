def skt_hash(ss, df, before, after, key_column=None):
    import time
    from typing import Callable, Mapping, Sequence, Tuple, Union

    import pandas as pd
    import requests
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.types import StringType, StructField, StructType

    from skt.vault_utils import get_secrets

    def generate_udf(
        auth_url: str,
        hash_url: str,
        unhash_url: str,
        client_id: str,
        client_secret: str,
    ) -> Tuple[Callable, Callable]:
        class LakeApi:
            BATCH_SIZE = 5000

            def __init__(
                self,
                auth_url: str,
                hash_url: str,
                unhash_url: str,
                client_id: str,
                client_secret: str,
            ):
                self._auth_url = auth_url
                self._hash_url = hash_url
                self._unhash_url = unhash_url
                self._client_id = client_id
                self._client_secret = client_secret
                self._auth_session = requests.Session()
                self._auth_session.auth = (self._client_id, self._client_secret)
                self._api_session = requests.Session()

            def close(self):
                self._auth_session.close()
                self._api_session.close()

            def refresh_access_token(self) -> str:
                token = self._get_access_token()
                self.set_access_token(token)
                print("Refreshed access token.")
                return token

            def set_access_token(self, token: str):
                self._api_session.headers.update(
                    {
                        "Authorization": f"Bearer {token}",
                    }
                )

            def __enter__(self) -> "LakeApi":
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                self.close()

            def _get_access_token(self, retry: int = 30, retry_delay: int = 2, timeout: int = 5) -> str:
                for i in range(retry + 1):
                    try:
                        response = self._auth_session.post(
                            url=self._auth_url,
                            data={"grant_type": "client_credentials"},
                            timeout=timeout,
                        )
                        response.raise_for_status()
                        return response.json()["access_token"]
                    except Exception as e:
                        print(f"Failed to get access token. Caused by {str(e)}. Retry {i + 1} times.")
                        time.sleep(retry_delay)
                raise Exception(f"Failed to get access token after {retry} retries.")

            def _call_lake_api(
                self,
                url: str,
                data: Mapping[str, Union[str, Sequence[str]]],
                key: str,
                retry: int,
                retry_delay: int = 2,
                timeout: int = 10,
            ) -> Sequence[str]:
                if not self._api_session.headers.get("Authorization"):
                    self.refresh_access_token()

                for i in range(retry + 1):
                    response = self._api_session.post(url=url, json=data, timeout=timeout)
                    try:
                        if response.status_code == 401:
                            self.refresh_access_token()

                        response.raise_for_status()

                        return [record[key] for record in response.json()["response"]]
                    except Exception as e:
                        print(f"Failed to call lake api. Caused by {str(e)}. Retry {i + 1} times.")
                        time.sleep(retry_delay)
                raise Exception(f"Failed to call lake api after {retry} retries.")

            def hashing(
                self,
                data: Sequence[str],
                type_: str = "s",
                retry: int = 5,
            ) -> Sequence[str]:
                return self._call_lake_api(
                    url=self._hash_url,
                    data={"type": type_, "unhashedValues": data},
                    key="hashedValue",
                    retry=retry,
                )

            def unhashing(
                self,
                data: Sequence[str],
                type_: str = "s",
                retry: int = 5,
            ) -> Sequence[str]:
                return self._call_lake_api(
                    url=self._unhash_url,
                    data={"type": type_, "hashedValues": data},
                    key="unhashedValue",
                    retry=retry,
                )

        def inner_hashing_udf(pdf: pd.DataFrame) -> pd.DataFrame:
            outputs = []
            with LakeApi(
                auth_url=auth_url,
                hash_url=hash_url,
                unhash_url=unhash_url,
                client_id=client_id,
                client_secret=client_secret,
            ) as lake_api:
                for i in range(0, len(pdf), lake_api.BATCH_SIZE):
                    value = pdf.loc[i : i + lake_api.BATCH_SIZE - 1, :]
                    value.loc[:, "lake_hash"] = lake_api.hashing(
                        data=list(value.loc[:, "lake_hash"]),
                    )
                    outputs.append(value)

            return pd.concat(outputs)

        def inner_unhashing_udf(pdf: pd.DataFrame) -> pd.DataFrame:
            outputs = []
            with LakeApi(
                auth_url=auth_url,
                hash_url=hash_url,
                unhash_url=unhash_url,
                client_id=client_id,
                client_secret=client_secret,
            ) as lake_api:
                for i in range(0, len(pdf), lake_api.BATCH_SIZE):
                    value = pdf.loc[i : i + lake_api.BATCH_SIZE - 1, :]
                    value.loc[:, "lake_unhash"] = lake_api.unhashing(data=list(value.loc[:, "lake_unhash"]))
                    outputs.append(value)

            return pd.concat(outputs)

        return inner_hashing_udf, inner_unhashing_udf

    secrets = get_secrets("lake/hash")

    hashing_func, unhashing_func = generate_udf(
        **secrets,
    )

    def get_latest_dt_from_mapping_table(ss: SparkSession) -> str:
        spark = ss
        partitions = spark.sql("show partitions aidp.svc_mgmt_num_mapping").collect()
        dts = [r.partition.split("=")[-1] for r in partitions]
        return sorted(dts, reverse=True)[0]

    def get_mapping_df(ss: SparkSession) -> DataFrame:
        spark = ss
        dt = get_latest_dt_from_mapping_table(spark)
        mapping_df = spark.sql(f" select raw, ye_hashed, lake_hashed from aidp.svc_mgmt_num_mapping where dt = {dt}")
        return mapping_df

    def get_select_hash_schema(df: DataFrame, key: str) -> str:
        sql = ""
        for col in df.columns:
            if col == f"lake_hashed_{key}":
                sql += f"case when a.lake_hashed_{key} is null then b.lake_hash else a.lake_hashed_{key} end as {key}"
            elif col == key:
                pass
            else:
                sql += "a." + col + ","

        return sql

    def get_select_unhash_schema(df: DataFrame, key: str) -> str:
        sql = ""
        for col in df.columns:
            if col == f"raw_{key}":
                sql += f"case when a.raw_{key} is null then b.lake_unhash else a.raw_{key} end as {key}"
            elif col == key:
                pass
            else:
                sql += "a." + col + ","

        return sql

    def lake_hash_to_sha256(ss: SparkSession, source_df: DataFrame, key: str) -> DataFrame:
        raw_df = lake_hash_to_raw(ss=ss, source_df=source_df, key=key)
        return raw_to_sha256(ss=ss, source_df=raw_df, key=key)

    def lake_hash_to_raw(ss: SparkSession, source_df: DataFrame, key: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")

        mapping_df = get_mapping_df(ss=spark)
        mapping_df.createOrReplaceTempView("mapping_table")

        joined_df = spark.sql(
            f"""
            select
                a.*,
                b.raw as raw_{key}
            from
                source_table a left outer join mapping_table b
                on a.{key} = b.lake_hashed
            """
        )
        joined_df.createOrReplaceTempView("joined_table")

        not_mapping = spark.sql(
            f"""
            select
                distinct
                {key} as svc_mgmt_num,
                {key} as lake_unhash,
                substr({key}, 9,3) as seed
            from
                joined_table
            where
                raw_{key} is null
                and {key} is not null
            """
        )

        if not_mapping.count() > 0:
            unhashed_df = not_mapping.groupby("seed").applyInPandas(
                unhashing_func,
                schema=StructType(
                    [
                        StructField("svc_mgmt_num", StringType(), True),
                        StructField("lake_unhash", StringType(), True),
                        StructField("seed", StringType(), True),
                    ]
                ),
            )
            unhashed_df.createOrReplaceTempView("unhashed_table")

            schema = get_select_unhash_schema(joined_df, key)

            result_df = spark.sql(
                f"""
                select
                    {schema}
                from
                    joined_table a left outer join unhashed_table b
                    on a.{key} = b.svc_mgmt_num
            """
            )

        else:
            result_df = joined_df.drop(key).withColumnRenamed(f"raw_{key}", key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")
        spark.catalog.dropTempView("joined_table")

        return result_df.drop("seed")

    def raw_to_sha256(ss: SparkSession, source_df: DataFrame, key: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")

        hashed_df = spark.sql(
            f"""
            select
                *,
                sha2({key}, 256) as sha256_{key}
            from
                source_table
            """
        )

        spark.catalog.dropTempView("source_table")
        return hashed_df.drop(key).withColumnRenamed(f"sha256_{key}", key)

    def raw_to_lake_hash(ss: SparkSession, source_df: DataFrame, key: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")

        mapping_df = get_mapping_df(ss=spark)
        mapping_df.createOrReplaceTempView("mapping_table")

        joined_df = spark.sql(
            f"""
            select
                a.*,
                b.lake_hashed as lake_hashed_{key}
            from
                source_table a left outer join mapping_table b
                on a.{key} = b.raw
        """
        )
        joined_df.createOrReplaceTempView("joined_table")

        not_mapping = spark.sql(
            f"""
            select
                distinct
                {key} as svc_mgmt_num,
                {key} as lake_hash,
                substr({key}, 9,3) as seed
            from
                joined_table
            where
                lake_hashed_{key} is null
                and {key} is not null
        """
        )

        if not_mapping.count() > 0:
            hashed_df = not_mapping.groupby("seed").applyInPandas(
                hashing_func,
                schema=StructType(
                    [
                        StructField("svc_mgmt_num", StringType(), True),
                        StructField("lake_hash", StringType(), True),
                        StructField("seed", StringType(), True),
                    ]
                ),
            )
            hashed_df.createOrReplaceTempView("hashed_table")

            schema = get_select_hash_schema(joined_df, key)
            result_df = spark.sql(
                f"""
                select
                    {schema}
                from
                    joined_table a left outer join hashed_table b
                    on a.{key} = b.svc_mgmt_num
            """
            )

        else:
            result_df = joined_df.drop(key).withColumnRenamed(f"lake_hashed_{key}", key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")
        spark.catalog.dropTempView("joined_table")

        return result_df.drop("seed")

    def sha256_to_raw(ss: SparkSession, source_df: DataFrame, key: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")

        mapping_df = get_mapping_df(ss=spark)
        mapping_df.createOrReplaceTempView("mapping_table")

        joined_df = spark.sql(
            f"""
            select
                a.*,
                b.raw as raw_{key}
            from
                source_table a left outer join mapping_table b
                on a.{key} = b.ye_hashed
        """
        )

        result_df = joined_df.drop(key).withColumnRenamed(f"raw_{key}", key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    def sha256_to_lake_hash(ss: SparkSession, source_df: DataFrame, key: str) -> DataFrame:
        spark = ss

        source_df.createOrReplaceTempView("source_table")

        mapping_df = get_mapping_df(ss=spark)
        mapping_df.createOrReplaceTempView("mapping_table")

        joined_df = spark.sql(
            f"""
            select
                a.*,
                b.lake_hashed as lake_hashed_{key}
            from
                source_table a left outer join mapping_table b
                on a.{key} = b.ye_hashed
        """
        )

        result_df = joined_df.drop(key).withColumnRenamed(f"lake_hashed_{key}", key)

        spark.catalog.dropTempView("source_table")
        spark.catalog.dropTempView("mapping_table")

        return result_df

    spark = ss
    key = key_column or "svc_mgmt_num"

    try:
        result_df: DataFrame = eval(f"{before}_to_{after}")(ss=spark, source_df=df, key=key)
        return result_df.select(df.columns)
    except NameError as e:
        print(
            f"ERROR : Could not convert data to '{before}' to '{after}'.  raw, lake_hash and sha256 are only available."
        )
        raise e
