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
