# Content Lengths Queries

### Story Content Lengths per Genre
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
            
			avgNumCharacters: { $avg: '$numCharacters'},
			avgNumLetters: { $avg: '$numLetters'},
			avgNumWords: { $avg: '$numWords'},
			avgNumSentences: { $avg: '$numSentences'},
            
			minNumCharacters: { $min: '$numCharacters'},
			minNumLetters: { $min: '$numLetters'},
			minNumWords: { $min: '$numWords'},
			minNumSentences: { $min: '$numSentences'},
            
			maxNumCharacters: { $max: '$numCharacters'},
			maxNumLetters: { $max: '$numLetters'},
			maxNumWords: { $max: '$numWords'},
			maxNumSentences: { $max: '$numSentences'}
		}
	},
    {
        $sort: { avgNumCharacters: -1 }
    },
	{
		$project: {
			avgNumCharacters: { $round: ['$avgNumCharacters', 2] },
			avgNumLetters: { $round: ['$avgNumLetters', 2] },
			avgNumWords: { $round: ['$avgNumWords', 2] },
			avgNumSentences: { $round: ['$avgNumSentences', 2] },
            
			minNumCharacters:1,
			minNumLetters: 1,
			minNumWords: 1,
			minNumSentences: 1,
            
			maxNumCharacters: 1,
			maxNumLetters: 1,
			maxNumWords: 1,
			maxNumSentences: 1
		}
	}
])
```

### Overall Story Content Lengths
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: null,
            
			avgNumCharacters: { $avg: '$numCharacters'},
			avgNumLetters: { $avg: '$numLetters'},
			avgNumWords: { $avg: '$numWords'},
			avgNumSentences: { $avg: '$numSentences'},
            
			minNumCharacters: { $min: '$numCharacters'},
			minNumLetters: { $min: '$numLetters'},
			minNumWords: { $min: '$numWords'},
			minNumSentences: { $min: '$numSentences'},
            
			maxNumCharacters: { $max: '$numCharacters'},
			maxNumLetters: { $max: '$numLetters'},
			maxNumWords: { $max: '$numWords'},
			maxNumSentences: { $max: '$numSentences'}
		}
	},
    {
        $sort: { avgNumCharacters: -1 }
    }
])
```


### Median Story Content Lengths per Genre
```javascript
let genres = ['Bücher', 'Prominente', 'Anime & Manga', 'Serien & Podcasts', 'Kino- & TV-Filme', 'Crossover', 'Computerspiele', 'Cartoons & Comics', 'Musicals', 'Andere Medien', 'Tabletop- & Rollenspiele']
let fields = ['numSentences', 'numWords', 'numLetters', 'numCharacters']
let count = 0
let result = []
let newDoc = {}
for (genre of genres) {
	newDoc = {genre: genre}
	for (f of fields) {
		count = db.stories.countDocuments({genre: genre})
		newDoc[f] = db.stories.find({genre: genre}).sort({f:1}).skip(parseInt(count / 2)).limit(1).toArray()[0][f]
	}
	result.push(newDoc)
}

// Genre, Sentences, Words, Letters, Characters
result.forEach((doc) => {
	print(doc.genre, doc.numSentences, doc.numWords, doc.numLetters, doc.numCharacters)
})
```


### Overall Median Story Content Length for Sentences
```javascript
let count = db.stories.countDocuments()
db.stories.find({}, {_id: 0, numSentences: 1}).sort({numSentences: 1}).skip(parseInt(count / 2)).limit(1)
```


### Story Content Lengths per Top 20 Fandoms
```javascript
let top20Fandoms = []
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
        $unwind: '$fandom'
    },
    {
        $sort : { frequency: -1 }
    },
	{
		$project: {
			fandom: 1
		}
	}
]).toArray().slice(0, 20).forEach((doc) => { top20Fandoms.push(doc.fandom) })

db.stories.aggregate([
	{
		$unwind: {
			path: '$fandoms',
			preserveNullAndEmptyArrays: true
		}
	},
	{
		$match: {
			'fandoms.tier1': { $in: top20Fandoms }
		}
	},
	{
		$group: {
			_id: '$fandoms.tier1',
			
			avgNumCharacters: { $avg: '$numCharacters'},
			avgNumLetters: { $avg: '$numLetters'},
			avgNumWords: { $avg: '$numWords'},
			avgNumSentences: { $avg: '$numSentences'},
			
			minNumCharacters: { $min: '$numCharacters'},
			minNumLetters: { $min: '$numLetters'},
			minNumWords: { $min: '$numWords'},
			minNumSentences: { $min: '$numSentences'},
			
			maxNumCharacters: { $max: '$numCharacters'},
			maxNumLetters: { $max: '$numLetters'},
			maxNumWords: { $max: '$numWords'},
			maxNumSentences: { $max: '$numSentences'}
		}
	},
    {
        $sort: { avgNumCharacters: -1 }
    },
	{
		$project: {
			avgNumCharacters: { $round: ['$avgNumCharacters', 2] },
			avgNumLetters: { $round: ['$avgNumLetters', 2] },
			avgNumWords: { $round: ['$avgNumWords', 2] },
			avgNumSentences: { $round: ['$avgNumSentences', 2] },
			
			minNumCharacters:1,
			minNumLetters: 1,
			minNumWords: 1,
			minNumSentences: 1,
			
			maxNumCharacters: 1,
			maxNumLetters: 1,
			maxNumWords: 1,
			maxNumSentences: 1
		}
	}
])
```
