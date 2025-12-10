# geometry.backend

## Setup

```
pip install requirements.txt
```

## Run

```
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```


## Using

- Enter [Swagger UI](http://localhost:8001/docs)

- Past your construction into the upload-construction endpoint
- Here's the example of construction: 
```json
{
  "name": "test123321",
  "figures": [
    {
      "type": "triangle",
      "name": "triangle_ABC",
      "edges": [
        {
          "vert1": "A",
          "vert2": "B",
          "length": {
            "value": 12.0,
            "way_of_measurement": "meters"
          }
        },
        {
          "vert1": "A", 
          "vert2": "C"
        }
      ]
    }
  ],
  "relationships": [
    {
      "type": "nonrole",
      "name": "equality",
      "source_entity": "AB",
      "target_entity": "AC",
      "oriented": false
    }
  ]
}
```

- After sending this construction you can find it in the KB under the name you have sent it with (test123321 for the example construction)

- As a response from the endpoint you will get parsed as JSON solving steps for the found task