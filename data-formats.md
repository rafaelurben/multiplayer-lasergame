# Data exchange formats

## Engine <-> Webserver

### Players

```json
[
    {
        "id": 0,
        "name": "Player 1",
        "team": 0
    },
    {
        "id": 1,
        "name": "Player 2",
        "team": 1
    }
]
```

### Blocks

```json
[
    {
        "id": 2,
        "team": 0,
        "owner": 3,
        "type": 1,
        "pos": {
            "x": 0,
            "y": 0
        },
        "rotation": 180
    },
    {
        "id": 3,
        "team": 1,
        "owner": 1,
        "type": 3,
        "pos": {
            "x": 10,
            "y": 5
        },
    }
]
```

#### Block types

```python
0: Empty
1: Wall
2: Emitter
3: Receiver
4: Wood
5: Mirror
6: Glass
```

### Lasers

(One element per emitted laser; team defines color.)

```json
[
    {
        "team": 0,
        "lines": [
            [[x1, y1, x2, y2], strength],
            [[x1, y1, x2, y2], strength],
            [[x1, y1, x2, y2], strength]
        ]
    },
    {
        "team": 1,
        "lines": [
            [[x1, y1, x2, y2], strength],
            [[x1, y1, x2, y2], strength],
            [[x1, y1, x2, y2], strength]
        ]
    }
]
```
