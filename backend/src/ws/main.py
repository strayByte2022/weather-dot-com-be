from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx

app = FastAPI()

KSQLDB_SERVER_URL = "http://localhost:8088"


@app.websocket("/ws/weather/average")
async def websocket_weather_average(websocket: WebSocket):
    await websocket.accept()
    query = """
    SELECT *
    FROM weather_10min_avg
    EMIT CHANGES;
    """

    payload = {
        "sql": query,
        "streamsProperties": {
            "ksql.query.push.v2.enabled": "true"
            # "ksql.streams.auto.offset.reset": "earliest"
        }
    }

    headers = {
        "Accept": "application/vnd.ksqlapi.delimited.v1"
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{KSQLDB_SERVER_URL}/query-stream",
                json=payload,
                headers=headers
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        await websocket.send_text(line)
    except WebSocketDisconnect:
        # Client disconnected; no action needed
        pass
    except Exception as e:
        await websocket.send_text(f"error: {str(e)}")
    finally:
        await websocket.close()
