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
				quantity: {$sum: 1}
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
		$group: {
			_id: '$pairings',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			pairing: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalStoryPairings]}, 100]}, 2]}
		}
	},
	{
		$sort: {frequency: -1}
	}
])
```

| frequency | pairing | percent |
| :--- | :--- | :--- |
| 276,188 | Generic | 66.5 |
| 117,051 | M/M | 28.18 |
| 14,784 | F/M | 3.56 |
| 2,826 | F/F | 0.68 |
| 2,702 | Multi | 0.65 |
| 1,059 | null | 0.25 |
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
				quantity: {$sum: 1}
			}
		}
	]).toArray()[0]['quantity']

db.stories.aggregate([
	{
		$group: {
			_id: '$rating',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			rating: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalStoryRatings]}, 100]}, 2]}
		}
	},
	{$sort: {frequency: -1}}
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
				quantity: {$sum: 1}
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
		$group: {
			_id: '$characters',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			character: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalStoryCharacters]}, 100]}, 2]}
		}
	},
	{$sort: {frequency: -1}}
])
```

| frequency | percent | rating |
| :--- | :--- | :--- |
| 188,704 | 45.7 | P12 |
| 118,480 | 28.69 | P16 |
| 67,995 | 16.47 | P18 |
| 33,654 | 8.15 | P6 |
| 2,223 | 0.54 | P18-AVL |
| 1,867 | 0.45 | Not Rated |

