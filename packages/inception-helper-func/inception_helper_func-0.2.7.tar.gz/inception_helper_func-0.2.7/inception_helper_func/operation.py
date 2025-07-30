import aiohttp
from fastapi import HTTPException


async def post_data(
    payload: dict, url: str, authorization: str, extra_headers: dict = {}
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to save data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def get_data(url: str, authorization: str, extra_headers: dict = {}):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to retrieve data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def put_data(
    payload: dict, url: str, authorization: str, extra_headers: dict = {}
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to update data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def delete_data(url: str, authorization: str, extra_headers: dict = {}):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to delete data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def patch_data(
    payload: dict, url: str, authorization: str, extra_headers: dict = {}
):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": authorization,
                    **extra_headers,
                },
            ) as response:
                if response.status in (200, 201):
                    return await response.json()

                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to patch data: {error_detail}",
                )
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Network error occurred on {url}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error occurred on {url}: {str(e)}"
        )


async def mongo_multi_delete(
    data_list: list,
    mongodb_connection,
    collection_name: str
):
    """
    Perform bulk delete operations in MongoDB.
    
    Args:
        data_list (list): List of dictionaries containing filter criteria for deletion
        mongodb_connection: MongoDB connection object
        collection_name (str): Name of the collection to perform operations on
    
    Returns:
        dict: Result of the bulk operation

    Example usage of multi_delete
    filters = [
        {"_id": "doc1"},
        {"status": "inactive"},
        {"age": {"$lt": 18}}
    ]
    result = await multi_delete(filters, mongodb_connection, "users")
    print(result)
    """
    try:
        collection = mongodb_connection[collection_name]
        operations = [{"deleteOne": {"filter": item}} for item in data_list]
        
        result = await collection.bulk_write(operations)
        return {
            "deleted_count": result.deleted_count,
            "acknowledged": result.acknowledged
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk delete operation: {str(e)}"
        )


async def mongo_multi_update(
    data_list: list,
    mongodb_connection,
    collection_name: str
):
    """
    Perform bulk update operations in MongoDB.
    
    Args:
        data_list (list): List of dictionaries containing filter and update operations
            Each item should have 'filter' and 'update' keys
        mongodb_connection: MongoDB connection object
        collection_name (str): Name of the collection to perform operations on
    
    Returns:
        dict: Result of the bulk operation

    Example usage of multi_update
    updates = [
        {
            "filter": {"_id": "doc1"},
            "update": {"$set": {"status": "active"}}
        },
        {
            "filter": {"age": {"$lt": 18}},
            "update": {"$set": {"category": "minor"}}
        }
    ]
    result = await multi_update(updates, mongodb_connection, "users")
    """
    try:
        collection = mongodb_connection[collection_name]
        operations = [
            {
                "updateOne": {
                    "filter": item["filter"],
                    "update": item["update"]
                }
            } for item in data_list
        ]
        
        result = await collection.bulk_write(operations)
        return {
            "modified_count": result.modified_count,
            "matched_count": result.matched_count,
            "acknowledged": result.acknowledged
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk update operation: {str(e)}"
        )


async def es_multi_delete(
    data_list: list,
    es_client,
    index_name: str
):
    """
    Perform bulk delete operations in Elasticsearch.
    
    Args:
        data_list (list): List of dictionaries containing document IDs or query criteria for deletion
        es_client: Elasticsearch client object
        index_name (str): Name of the index to perform operations on
    
    Returns:
        dict: Result of the bulk operation

    Example usage of es_multi_delete:
    # Delete by document IDs
    doc_ids = ["doc1", "doc2", "doc3"]
    result = await es_multi_delete(doc_ids, es_client, "users")
    
    # Delete by query criteria
    queries = [
        {"term": {"status": "inactive"}},
        {"range": {"age": {"lt": 18}}}
    ]
    result = await es_multi_delete(queries, es_client, "users")
    """
    try:
        bulk_operations = []
        
        for item in data_list:
            if isinstance(item, str):
                # If item is a string, treat it as a document ID
                bulk_operations.extend([
                    {"delete": {"_index": index_name, "_id": item}}
                ])
            else:
                # If item is a dict, treat it as a query
                bulk_operations.extend([
                    {"delete_by_query": {"index": index_name, "query": item}}
                ])
        
        if not bulk_operations:
            return {"deleted": 0, "errors": False}
            
        result = await es_client.bulk(operations=bulk_operations)
        
        if result.get("errors"):
            raise Exception("Some operations failed during bulk delete")
            
        return {
            "deleted": len(data_list),
            "errors": False,
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk delete operation in Elasticsearch: {str(e)}"
        )


async def es_multi_update(
    data_list: list,
    es_client,
    index_name: str
):
    """
    Perform bulk update operations in Elasticsearch.
    
    Args:
        data_list (list): List of dictionaries containing document IDs and update operations
            Each item should have 'id' and 'doc' keys, or 'query' and 'script' keys
        es_client: Elasticsearch client object
        index_name (str): Name of the index to perform operations on
    
    Returns:
        dict: Result of the bulk operation

    Example usage of es_multi_update:
    # Update by document IDs
    updates = [
        {
            "id": "doc1",
            "doc": {"status": "active", "last_updated": "2024-03-20"}
        },
        {
            "id": "doc2",
            "doc": {"status": "inactive", "last_updated": "2024-03-20"}
        }
    ]
    result = await es_multi_update(updates, es_client, "users")
    
    # Update by query
    updates = [
        {
            "query": {"term": {"status": "pending"}},
            "script": {
                "source": "ctx._source.status = 'active'; ctx._source.last_updated = '2024-03-20'"
            }
        }
    ]
    result = await es_multi_update(updates, es_client, "users")
    """
    try:
        bulk_operations = []
        
        for item in data_list:
            if "id" in item and "doc" in item:
                # Update by document ID
                bulk_operations.extend([
                    {"update": {"_index": index_name, "_id": item["id"]}},
                    {"doc": item["doc"]}
                ])
            elif "query" in item and "script" in item:
                # Update by query
                bulk_operations.extend([
                    {"update_by_query": {
                        "index": index_name,
                        "query": item["query"],
                        "script": item["script"]
                    }}
                ])
        
        if not bulk_operations:
            return {"updated": 0, "errors": False}
            
        result = await es_client.bulk(operations=bulk_operations)
        
        if result.get("errors"):
            raise Exception("Some operations failed during bulk update")
            
        return {
            "updated": len(data_list),
            "errors": False,
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk update operation in Elasticsearch: {str(e)}"
        )


async def pg_multi_delete(
    data_list: list,
    pg_pool,
    table_name: str,
    id_column: str = "id"
):
    """
    Perform bulk delete operations in PostgreSQL.
    
    Args:
        data_list (list): List of values to match against the id_column for deletion
        pg_pool: PostgreSQL connection pool
        table_name (str): Name of the table to perform operations on
        id_column (str): Name of the column to match against (default: "id")
    
    Returns:
        dict: Result of the bulk operation

    Example usage of pg_multi_delete:
    # Delete by IDs
    ids = [1, 2, 3]
    result = await pg_multi_delete(ids, pg_pool, "users")
    
    # Delete by specific column values
    values = ["user1", "user2", "user3"]
    result = await pg_multi_delete(values, pg_pool, "users", "username")
    """
    try:
        if not data_list:
            return {"deleted": 0, "errors": False}

        # Create placeholders for the IN clause
        placeholders = ','.join(['%s'] * len(data_list))
        
        # Construct the DELETE query
        query = f"""
            DELETE FROM {table_name}
            WHERE {id_column} = ANY(%s)
            RETURNING {id_column}
        """
        
        async with pg_pool.acquire() as conn:
            result = await conn.fetch(query, data_list)
            
        return {
            "deleted": len(result),
            "errors": False,
            "deleted_ids": [row[id_column] for row in result]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk delete operation in PostgreSQL: {str(e)}"
        )


async def pg_multi_update(
    data_list: list,
    pg_pool,
    table_name: str,
    id_column: str = "id"
):
    """
    Perform bulk update operations in PostgreSQL.
    
    Args:
        data_list (list): List of dictionaries containing id and update data
            Each item should have 'id' and 'data' keys where 'data' is a dict of column-value pairs
        pg_pool: PostgreSQL connection pool
        table_name (str): Name of the table to perform operations on
        id_column (str): Name of the column to match against (default: "id")
    
    Returns:
        dict: Result of the bulk operation

    Example usage of pg_multi_update:
    # Update multiple records
    updates = [
        {
            "id": 1,
            "data": {
                "status": "active",
                "last_updated": "2024-03-20"
            }
        },
        {
            "id": 2,
            "data": {
                "status": "inactive",
                "last_updated": "2024-03-20"
            }
        }
    ]
    result = await pg_multi_update(updates, pg_pool, "users")
    """
    try:
        if not data_list:
            return {"updated": 0, "errors": False}

        async with pg_pool.acquire() as conn:
            updated_ids = []
            
            for item in data_list:
                # Extract the ID and update data
                record_id = item['id']
                update_data = item['data']
                
                # Construct the SET clause
                set_clause = ', '.join([f"{k} = %s" for k in update_data.keys()])
                
                # Construct the UPDATE query
                query = f"""
                    UPDATE {table_name}
                    SET {set_clause}
                    WHERE {id_column} = %s
                    RETURNING {id_column}
                """
                
                # Combine the values for the query
                values = list(update_data.values()) + [record_id]
                
                # Execute the update
                result = await conn.fetchrow(query, *values)
                if result:
                    updated_ids.append(result[id_column])
            
        return {
            "updated": len(updated_ids),
            "errors": False,
            "updated_ids": updated_ids
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform bulk update operation in PostgreSQL: {str(e)}"
        )



