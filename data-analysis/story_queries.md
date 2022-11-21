# Story Attributes Queries

### Pairing Frequencies
```javascript
let totalStoryPairings = 
db.stories.aggregate([
	{
        $unwind: {
            path: '$pairings',
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group: {
            _id: null,
            quantity: { $sum: 1 }
        }
    }
]).toArray()[0]['quantity']

db.stories.aggregate([
    {
        $unwind: {
            path: '$pairings',
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group : {
            _id: '$pairings',
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            pairing: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryPairings ]}, 100 ]}, 2]}
        }
    },
    {
        $sort : { frequency: -1 }
    }
])
```
| frequency | pairing | percent |
| :--- | :--- | :--- |
| 276188 | Generic | 66.5 |
| 117051 | M/M | 28.18 |
| 14784 | F/M | 3.56 |
| 2826 | F/F | 0.68 |
| 2702 | Multi | 0.65 |
| 1059 | null | 0.25 |
| 693 | Other | 0.17 |


### Rating Frequencies
```javascript
let totalStoryRatings = 
db.stories.aggregate([
	{
        $unwind: {
            path: '$ratings',
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group: {
            _id: null,
            quantity: { $sum: 1 }
        }
    }
]).toArray()[0]['quantity']

db.stories.aggregate([
    {
        $group : {
            _id: '$rating',
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            rating: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryRatings ]}, 100 ]}, 2]}
        }
    },
    { $sort : { frequency: -1 } }
])
```

### Character Frequencies
```javascript
let totalStoryCharacters =
db.stories.aggregate([
    {
        $unwind: {
            path: '$characters',
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group: {
            _id: null,
            quantity: { $sum: 1 }
        }
    }
]).toArray()[0]['quantity']

db.stories.aggregate([
    {
        $unwind: {
            path: '$characters',
            preserveNullAndEmptyArrays: true
        }
    },
{
        $group : {
            _id: '$characters',
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            character: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryCharacters ]}, 100 ]}, 2]}
        }
    },
    { $sort : { frequency: -1 } }
])
```
| frequency | percent | rating |
| :--- | :--- | :--- |
| 188704 | 45.7 | P12 |
| 118480 | 28.69 | P16 |
| 67995 | 16.47 | P18 |
| 33654 | 8.15 | P6 |
| 2223 | 0.54 | P18-AVL |
| 1867 | 0.45 | Not Rated |

