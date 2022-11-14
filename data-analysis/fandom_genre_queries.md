# Fandom and Genre Queries

### Fandom Frequencies
```javascript
let totalStoryFandoms =
db.stories.aggregate([
    {
        $unwind: {
            path: '$fandoms',
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
            path: '$fandoms',
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group : {
            _id: '$fandoms',
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            fandom: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryFandoms ]}, 100 ]}, 2]}
        }
    },
    {
        $sort : { frequency: -1 }
    }
])
```

### Fandom Tier1 Frequencies
```javascript
let totalStoryTier1Fandoms = 
db.stories.aggregate([
    {
        $unwind: {
            path: '$fandoms.tier1',
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
            path: '$fandoms.tier1',
            preserveNullAndEmptyArrays: true
        }
    },
    {
        $group : {
            _id: '$fandoms.tier1',
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            fandom: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryTier1Fandoms ]}, 100 ]}, 2]}
        }
    },
    {
        $sort : { frequency: -1 }
    }
])
```

### Genre Frequencies
```javascript
let totalStories = db.stories.countDocuments({})

db.stories.aggregate([
    {
        $group : {
            _id: '$genre',
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            genre: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStories ]}, 100 ]}, 2]}
        }
    },
    {
        $sort : { frequency: -1 }
    }
])
```

### Most Used Genre per Fandom
```javascript
db.stories.aggregate([
	{
		$unwind: {
			path: '$fandoms',
			preserveNullAndEmptyArrays: true
		}
	},
	{
        $group : {
            _id: { fandom: '$fandoms.tier1', genre: '$genre' },
            quantity: { $sum: 1 }
        }
    },
    {
        $project: {
            _id: 0,
            fandom: '$_id.fandom',
            genre: '$_id.genre',
            frequency: '$quantity',
        }
    },
    {
        $group: {
            _id: '$genre',
            maxScores: {
                $max: {
                    frequency: '$frequency', fandom: '$fandom'
                }
            }
        }
    },
    {
        $project: {
            _id: 0,
            genre: '$_id',
            fandom: '$maxScores.fandom',
            frequency: '$maxScores.frequency'

        }
    },
    {
        $sort: { frequency: -1 }
    }
])
```

### Genre Share per Source
```javascript
let genres = ['Bücher', 'Prominente', 'Anime & Manga', 'Serien & Podcasts', 'Kino- & TV-Filme', 'Crossover', 'Computerspiele', 'Cartoons & Comics', 'Musicals', 'Andere Medien', 'Tabletop- & Rollenspiele']
let totalStoriesFF = db.stories.countDocuments({ source: 'FanFiktion' })
let totalStoriesAO3 = db.stories.countDocuments({ source: 'ArchiveOfOurOwn' })

db.stories.aggregate([
	{
		$match: {
			'genre': genres[0]
		}
	},
	{
		$group: {
			_id: '$source',
			count: { $sum: 1 }
		}
	},
	{
		$project: {
			_id: 0,
			source: '$_id',
			count: 1,
			percent: { $round: [{ $multiply: [{ $divide: [ '$count', { $cond: { if: { $eq: ['$_id', 'FanFiktion'] }, then: totalStoriesFF, else: totalStoriesAO3 } } ]}, 100 ]}, 2]}
		}
	}
])
```

### Top Fandoms on FanFiktion.de per Genre
```javascript
let totalStoriesFF = db.stories.countDocuments({ source: 'FanFiktion' })

db.stories.aggregate([
	{
		$match: {
			source: 'FanFiktion'
		}
	},
	{
		$group: {
			_id: '$fandoms.tier1',
			count: { $sum: 1 }
		}
	},
	{
		$unwind: '$_id'
	},
	{
		$project: {
			_id: 0,
			fandom: '$_id',
			count: 1,
			percent: { $round: [{ $multiply: [{ $divide: [ '$count', totalStoriesFF ]}, 100 ]}, 2]}
		}
	},
	{
		$sort: { count: -1 }
	}
])
```

### Top Fandoms on ArchiveOfOurOwn per Genre
```javascript
let totalStoriesAO3 = db.stories.countDocuments({ source: 'ArchiveOfOurOwn' })

db.stories.aggregate([
	{
		$match: {
			source: 'ArchiveOfOurOwn'
		}
	},
	{
		$unwind: '$fandoms'
	},
	{
		$group: {
			_id: '$fandoms.tier1',
			count: { $sum: 1 }
		}
	},
	{
		$project: {
			_id: 0,
			fandom: '$_id',
			count: 1,
			percent: { $round: [{ $multiply: [{ $divide: [ '$count', totalStoriesAO3 ]}, 100 ]}, 2]}
		}
	},
	{
		$sort: { count: -1 }
	}
])
```