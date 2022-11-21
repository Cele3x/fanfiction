# Content Lengths Queries

### Story Content Lengths per Genre

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',

			avgNumCharacters: {$avg: '$numCharacters'},
			avgNumLetters: {$avg: '$numLetters'},
			avgNumWords: {$avg: '$numWords'},
			avgNumSentences: {$avg: '$numSentences'},

			minNumCharacters: {$min: '$numCharacters'},
			minNumLetters: {$min: '$numLetters'},
			minNumWords: {$min: '$numWords'},
			minNumSentences: {$min: '$numSentences'},

			maxNumCharacters: {$max: '$numCharacters'},
			maxNumLetters: {$max: '$numLetters'},
			maxNumWords: {$max: '$numWords'},
			maxNumSentences: {$max: '$numSentences'}
		}
	},
	{
		$sort: {avgNumCharacters: -1}
	},
	{
		$project: {
			avgNumCharacters: {$round: ['$avgNumCharacters', 2]},
			avgNumLetters: {$round: ['$avgNumLetters', 2]},
			avgNumWords: {$round: ['$avgNumWords', 2]},
			avgNumSentences: {$round: ['$avgNumSentences', 2]},

			minNumCharacters: 1,
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
| \_id | avgNumCharacters | avgNumLetters | avgNumSentences | avgNumWords | maxNumCharacters | maxNumLetters | maxNumSentences | maxNumWords | minNumCharacters | minNumLetters | minNumSentences | minNumWords |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Bücher | 89005.34 | 71239.64 | 1259.67 | 14335.97 | 25734178 | 20753491 | 200957 | 4106713 | 33 | 28 | 1 | 3 |
| Tabletop- & Rollenspiele | 88738.98 | 72186.45 | 1091.77 | 13835.51 | 2791133 | 2303344 | 33525 | 417251 | 190 | 152 | 2 | 32 |
| Crossover | 81900.17 | 65343.83 | 1208.26 | 13167.38 | 6620926 | 5376125 | 70860 | 1023615 | 117 | 54 | 1 | 11 |
| Computerspiele | 79475.17 | 63580.37 | 1143.17 | 12787.91 | 6876345 | 5563712 | 99042 | 1083004 | 25 | 21 | 1 | 5 |
| Musicals | 76496.29 | 61124.63 | 1118.16 | 12289.99 | 4944263 | 3987347 | 49774 | 772675 | 335 | 279 | 5 | 57 |
| Cartoons & Comics | 67819.61 | 54248.51 | 963.6 | 10932.18 | 3434633 | 2769029 | 62041 | 536037 | 22 | 15 | 1 | 4 |
| Kino- & TV-Filme | 67456.52 | 53995.21 | 950.98 | 10864.29 | 4353542 | 3448984 | 66920 | 695287 | 43 | 22 | 1 | 4 |
| Serien & Podcasts | 64783.3 | 51675.03 | 951.04 | 10506.24 | 13400239 | 10569451 | 180615 | 2016477 | 42 | 33 | 1 | 6 |
| Andere Medien | 45450.7 | 36497.45 | 610.98 | 7298.69 | 2351701 | 1878396 | 33162 | 375075 | 24 | 20 | 1 | 1 |
| Anime & Manga | 25836.35 | 20631.88 | 371.46 | 4181.77 | 8446766 | 6656468 | 150904 | 1452152 | 32 | 27 | 1 | 2 |
| Prominente | 13568.8 | 10806.14 | 196.63 | 2221.31 | 2672691 | 2127786 | 38991 | 439905 | 56 | 43 | 1 | 7 |


### Overall Story Content Lengths

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: null,

			avgNumCharacters: {$avg: '$numCharacters'},
			avgNumLetters: {$avg: '$numLetters'},
			avgNumWords: {$avg: '$numWords'},
			avgNumSentences: {$avg: '$numSentences'},

			minNumCharacters: {$min: '$numCharacters'},
			minNumLetters: {$min: '$numLetters'},
			minNumWords: {$min: '$numWords'},
			minNumSentences: {$min: '$numSentences'},

			maxNumCharacters: {$max: '$numCharacters'},
			maxNumLetters: {$max: '$numLetters'},
			maxNumWords: {$max: '$numWords'},
			maxNumSentences: {$max: '$numSentences'}
		}
	},
	{
		$project: {
			_id: 0,
			avgNumCharacters: 1,
			avgNumLetters: 1,
			avgNumWords: 1,
			avgNumSentences: 1,
			minNumCharacters: 1,
			minNumLetters: 1,
			minNumWords: 1,
			minNumSentences: 1,
			maxNumCharacters: 1,
			maxNumLetters: 1,
			maxNumWords: 1,
			maxNumSentences: 1
		}
	},
	{
		$sort: {avgNumCharacters: -1}
	}
])
```
| avgNumCharacters | avgNumLetters | avgNumSentences | avgNumWords | maxNumCharacters | maxNumLetters | maxNumSentences | maxNumWords | minNumCharacters | minNumLetters | minNumSentences | minNumWords |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 52565.91507859819 | 42022.92238746691 | 752.3567953347234 | 8487.086095954935 | 25734178 | 20753491 | 200957 | 4106713 | 22 | 15 | 1 | 1 |


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
		newDoc[f] = db.stories.find({genre: genre}).sort({f: 1}).skip(parseInt(count / 2)).limit(1).toArray()[0][f]
	}
	result.push(newDoc)
}

// Genre, Sentences, Words, Letters, Characters
result.forEach((doc) => {
	print(doc.genre, doc.numSentences, doc.numWords, doc.numLetters, doc.numCharacters)
})
```
| genre                    | numSentences | numWords | numLetters | numCharacters |
|:-------------------------| :--- | :--- | :--- | :--- |
| Bücher                   | 1777 | 21389 | 107618 | 133041 |
| Prominente               | 110 | 1351 | 6510 | 8210 |
| Anime & Manga            | 101 | 812 | 4248 | 5460 |
| Serien & Podcasts        | 33 | 224 | 1016 | 1440 |
| Kino- & TV-Filme         | 197 | 3155 | 15256 | 19193 |
| Crossover                | 1037 | 9897 | 46485 | 58682 |
| Computerspiele           | 98 | 1423 | 7672 | 9363 |
| Cartoons & Comics        | 318 | 3230 | 16111 | 20588 |
| Musicals                 | 19911 | 243903 | 1221731 | 1523534 |
| Andere Medien            | 334 | 3263 | 16298 | 20096 |
| Tabletop- & Rollenspiele | 70 | 788 | 3746 | 4719 |


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
				quantity: {$sum: 1}
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
		$group: {
			_id: '$fandoms.tier1',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			fandom: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalStoryTier1Fandoms]}, 100]}, 2]}
		}
	},
	{
		$unwind: '$fandom'
	},
	{
		$sort: {frequency: -1}
	},
	{
		$project: {
			fandom: 1
		}
	}
]).toArray().slice(0, 20).forEach((doc) => {
	top20Fandoms.push(doc.fandom)
})

db.stories.aggregate([
	{
		$unwind: {
			path: '$fandoms',
			preserveNullAndEmptyArrays: true
		}
	},
	{
		$match: {
			'fandoms.tier1': {$in: top20Fandoms}
		}
	},
	{
		$group: {
			_id: '$fandoms.tier1',

			avgNumCharacters: {$avg: '$numCharacters'},
			avgNumLetters: {$avg: '$numLetters'},
			avgNumWords: {$avg: '$numWords'},
			avgNumSentences: {$avg: '$numSentences'},

			minNumCharacters: {$min: '$numCharacters'},
			minNumLetters: {$min: '$numLetters'},
			minNumWords: {$min: '$numWords'},
			minNumSentences: {$min: '$numSentences'},

			maxNumCharacters: {$max: '$numCharacters'},
			maxNumLetters: {$max: '$numLetters'},
			maxNumWords: {$max: '$numWords'},
			maxNumSentences: {$max: '$numSentences'}
		}
	},
	{
		$sort: {avgNumCharacters: -1}
	},
	{
		$project: {
			avgNumCharacters: {$round: ['$avgNumCharacters', 2]},
			avgNumLetters: {$round: ['$avgNumLetters', 2]},
			avgNumWords: {$round: ['$avgNumWords', 2]},
			avgNumSentences: {$round: ['$avgNumSentences', 2]},

			minNumCharacters: 1,
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

| \_id | avgNumCharacters | avgNumLetters | avgNumSentences | avgNumWords | maxNumCharacters | maxNumLetters | maxNumSentences | maxNumWords | minNumCharacters | minNumLetters | minNumSentences | minNumWords |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Bis\(s\) | 118583.63 | 94277.52 | 1835.74 | 19517.86 | 7672715 | 6074848 | 108300 | 1209756 | 98 | 78 | 1 | 15 |
| J.R.R. Tolkien | 96393.21 | 77413.4 | 1290.21 | 15446.36 | 5591193 | 4514123 | 68532 | 877764 | 88 | 78 | 1 | 11 |
| Harry Potter | 91742.23 | 73538.44 | 1266.61 | 14680.55 | 25734178 | 20753491 | 200957 | 4106713 | 33 | 28 | 1 | 4 |
| Crossover | 80841.26 | 64535.4 | 1172.98 | 13003.64 | 6620926 | 5376125 | 70860 | 1023615 | 171 | 54 | 1 | 11 |
| Yu-Gi-Oh! | 76420.47 | 60913.8 | 1118.92 | 12412.64 | 8446766 | 6656468 | 150904 | 1452152 | 144 | 117 | 2 | 25 |
| Die Tribute von Panem | 72600.06 | 58055.64 | 1059.12 | 11845.5 | 3370560 | 2645898 | 69343 | 567598 | 262 | 212 | 1 | 47 |
| Star Wars | 70889.94 | 57063.5 | 964.17 | 11217.44 | 3220388 | 2605818 | 38728 | 492374 | 135 | 111 | 2 | 3 |
| Sherlock BBC | 69791.13 | 55857.93 | 1018.29 | 11075.42 | 13400239 | 10569451 | 180615 | 2016477 | 196 | 162 | 3 | 26 |
| Marvel | 68697.07 | 54935.45 | 974.26 | 11105.65 | 2606735 | 2063287 | 43564 | 412556 | 22 | 15 | 1 | 4 |
| Supernatural | 58701.63 | 46886 | 839.69 | 9558.73 | 5035050 | 4072887 | 72469 | 831216 | 74 | 59 | 1 | 12 |
| Navy CIS | 53476.68 | 42540.9 | 778.2 | 8755.38 | 3048838 | 2463697 | 44368 | 494977 | 270 | 195 | 5 | 43 |
| Rick Riordan | 50295.63 | 40046.54 | 769.2 | 8131.65 | 1744938 | 1406686 | 26671 | 274110 | 194 | 163 | 1 | 28 |
| Sport | 14053.99 | 11172.62 | 201.91 | 2285.28 | 1513505 | 1227765 | 17525 | 243717 | 101 | 81 | 1 | 10 |
| Schauspieler | 13124.76 | 10466.56 | 183.31 | 2146.72 | 1298473 | 1039703 | 16032 | 209582 | 120 | 92 | 1 | 18 |
| One Piece | 12953.07 | 10358.58 | 180.18 | 2098.26 | 3570997 | 2898607 | 33455 | 568899 | 169 | 132 | 1 | 18 |
| Inu Yasha | 12750.72 | 10196.33 | 180.17 | 2060.05 | 4726773 | 3797752 | 47499 | 758156 | 148 | 117 | 1 | 24 |
| Naruto | 11900.45 | 9499.53 | 172.43 | 1926.19 | 1751321 | 1407521 | 23724 | 286374 | 115 | 84 | 1 | 14 |
| Musik | 11473.89 | 9142.27 | 165.49 | 1878.21 | 2213660 | 1775830 | 27185 | 357361 | 72 | 56 | 1 | 10 |
| Detektiv Conan | 9367.26 | 7479.74 | 135.28 | 1516.4 | 954409 | 771107 | 11521 | 153442 | 160 | 129 | 1 | 24 |
| Internet-Stars | 7350.28 | 5839.96 | 114.25 | 1203.03 | 1534964 | 1199951 | 30568 | 257487 | 99 | 77 | 1 | 14 |

