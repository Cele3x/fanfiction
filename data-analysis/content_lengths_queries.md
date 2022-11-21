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

| genre                    | avgNumCharacters | avgNumLetters | avgNumSentences | avgNumWords | maxNumCharacters | maxNumLetters | maxNumSentences | maxNumWords | minNumCharacters | minNumLetters | minNumSentences | minNumWords |
|:-------------------------|:-----------------|:--------------|:----------------|:------------|:-----------------|:--------------|:----------------|:------------|:-----------------|:--------------|:----------------|:------------|
| Bücher                   | 89,005.34        | 71,239.64     | 1,259.67        | 14,335.97   | 25,734,178       | 20,753,491    | 200,957         | 4,106,713   | 33               | 28            | 1               | 3           |
| Tabletop- & Rollenspiele | 88,738.98        | 72,186.45     | 1,091.77        | 13,835.51   | 2,791,133        | 2,303,344     | 33,525          | 417,251     | 190              | 152           | 2               | 32          |
| Crossover                | 81,900.17        | 65,343.83     | 1,208.26        | 13,167.38   | 6,620,926        | 5,376,125     | 70,860          | 1,023,615   | 117              | 54            | 1               | 11          |
| Computerspiele           | 79,475.17        | 63,580.37     | 1,143.17        | 12,787.91   | 6,876,345        | 5,563,712     | 99,042          | 1,083,004   | 25               | 21            | 1               | 5           |
| Musicals                 | 76,496.29        | 61,124.63     | 1,118.16        | 12,289.99   | 4,944,263        | 3,987,347     | 49,774          | 772,675     | 335              | 279           | 5               | 57          |
| Cartoons & Comics        | 67,819.61        | 54,248.51     | 963.6           | 10,932.18   | 3,434,633        | 2,769,029     | 62,041          | 536,037     | 22               | 15            | 1               | 4           |
| Kino- & TV-Filme         | 67,456.52        | 53,995.21     | 950.98          | 10,864.29   | 4,353,542        | 3,448,984     | 66,920          | 695,287     | 43               | 22            | 1               | 4           |
| Serien & Podcasts        | 64,783.3         | 51,675.03     | 951.04          | 10,506.24   | 13,400,239       | 10,569,451    | 180,615         | 2,016,477   | 42               | 33            | 1               | 6           |
| Andere Medien            | 45,450.7         | 36,497.45     | 610.98          | 7,298.69    | 2,351,701        | 1,878,396     | 33,162          | 375,075     | 24               | 20            | 1               | 1           |
| Anime & Manga            | 25,836.35        | 20,631.88     | 371.46          | 4,181.77    | 8,446,766        | 6,656,468     | 150,904         | 1,452,152   | 32               | 27            | 1               | 2           |
| Prominente               | 13,568.8         | 10,806.14     | 196.63          | 2,221.31    | 2,672,691        | 2,127,786     | 38,991          | 439,905     | 56               | 43            | 1               | 7           |

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
|:-----------------|:--------------|:----------------|:------------|:-----------------|:--------------|:----------------|:------------|:-----------------|:--------------|:----------------|:------------|
| 52,565.92        | 42,022.92     | 752.36          | 8,487.09    | 25,734,178       | 20,753,491    | 200,957         | 4,106,713   | 22               | 15            | 1               | 1           |

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
|:-------------------------|:-------------|:---------|:-----------|:--------------|
| Bücher                   | 1,777        | 21,389   | 107,618    | 133,041       |
| Prominente               | 110          | 1,351    | 6,510      | 8,210         |
| Anime & Manga            | 101          | 812      | 4,248      | 5,460         |
| Serien & Podcasts        | 33           | 224      | 1,016      | 1,440         |
| Kino- & TV-Filme         | 197          | 3,155    | 15,256     | 19,193        |
| Crossover                | 1,037        | 9,897    | 46,485     | 58,682        |
| Computerspiele           | 98           | 1,423    | 7,672      | 9,363         |
| Cartoons & Comics        | 318          | 3,230    | 16,111     | 20,588        |
| Musicals                 | 19,911       | 243,903  | 1,221,731  | 1,523,534     |
| Andere Medien            | 334          | 3,263    | 16,298     | 20,096        |
| Tabletop- & Rollenspiele | 70           | 788      | 3,746      | 4,719         |

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

| \_id                  | avgNumCharacters | avgNumLetters | avgNumSentences | avgNumWords | maxNumCharacters | maxNumLetters | maxNumSentences | maxNumWords | minNumCharacters | minNumLetters | minNumSentences | minNumWords |
|:----------------------|:-----------------|:--------------|:----------------|:------------|:-----------------|:--------------|:----------------|:------------|:-----------------|:--------------|:----------------|:------------|
| Bis\(s\)              | 118,583.63       | 94,277.52     | 1,835.74        | 19,517.86   | 7,672,715        | 6,074,848     | 108,300         | 1,209,756   | 98               | 78            | 1               | 15          |
| J.R.R. Tolkien        | 96,393.21        | 77,413.4      | 1,290.21        | 15,446.36   | 5,591,193        | 4,514,123     | 68,532          | 877,764     | 88               | 78            | 1               | 11          |
| Harry Potter          | 91,742.23        | 73,538.44     | 1,266.61        | 14,680.55   | 25,734,178       | 20,753,491    | 200,957         | 4,106,713   | 33               | 28            | 1               | 4           |
| Crossover             | 80,841.26        | 64,535.4      | 1,172.98        | 13,003.64   | 6,620,926        | 5,376,125     | 70,860          | 1,023,615   | 171              | 54            | 1               | 11          |
| Yu-Gi-Oh!             | 76,420.47        | 60,913.8      | 1,118.92        | 12,412.64   | 8,446,766        | 6,656,468     | 150,904         | 1,452,152   | 144              | 117           | 2               | 25          |
| Die Tribute von Panem | 72,600.06        | 58,055.64     | 1,059.12        | 11,845.5    | 3,370,560        | 2,645,898     | 69,343          | 567,598     | 262              | 212           | 1               | 47          |
| Star Wars             | 70,889.94        | 57,063.5      | 964.17          | 11,217.44   | 3,220,388        | 2,605,818     | 38,728          | 492,374     | 135              | 111           | 2               | 3           |
| Sherlock BBC          | 69,791.13        | 55,857.93     | 1,018.29        | 11,075.42   | 13,400,239       | 10,569,451    | 180,615         | 2,016,477   | 196              | 162           | 3               | 26          |
| Marvel                | 68,697.07        | 54,935.45     | 974.26          | 11,105.65   | 2,606,735        | 2,063,287     | 43,564          | 412,556     | 22               | 15            | 1               | 4           |
| Supernatural          | 58,701.63        | 46,886        | 839.69          | 9,558.73    | 5,035,050        | 4,072,887     | 72,469          | 831,216     | 74               | 59            | 1               | 12          |
| Navy CIS              | 53,476.68        | 42,540.9      | 778.2           | 8,755.38    | 3,048,838        | 2,463,697     | 44,368          | 494,977     | 270              | 195           | 5               | 43          |
| Rick Riordan          | 50,295.63        | 40,046.54     | 769.2           | 8,131.65    | 1,744,938        | 1,406,686     | 26,671          | 274,110     | 194              | 163           | 1               | 28          |
| Sport                 | 14,053.99        | 11,172.62     | 201.91          | 2,285.28    | 1,513,505        | 1,227,765     | 17,525          | 243,717     | 101              | 81            | 1               | 10          |
| Schauspieler          | 13,124.76        | 10,466.56     | 183.31          | 2,146.72    | 1,298,473        | 1,039,703     | 16,032          | 209,582     | 120              | 92            | 1               | 18          |
| One Piece             | 12,953.07        | 10,358.58     | 180.18          | 2,098.26    | 3,570,997        | 2,898,607     | 33,455          | 568,899     | 169              | 132           | 1               | 18          |
| Inu Yasha             | 12,750.72        | 10,196.33     | 180.17          | 2,060.05    | 4,726,773        | 3,797,752     | 47,499          | 758,156     | 148              | 117           | 1               | 24          |
| Naruto                | 11,900.45        | 9,499.53      | 172.43          | 1,926.19    | 1,751,321        | 1,407,521     | 23,724          | 286,374     | 115              | 84            | 1               | 14          |
| Musik                 | 11,473.89        | 9,142.27      | 165.49          | 1,878.21    | 2,213,660        | 1,775,830     | 27,185          | 357,361     | 72               | 56            | 1               | 10          |
| Detektiv Conan        | 9,367.26         | 7,479.74      | 135.28          | 1,516.4     | 954,409          | 771,107       | 11,521          | 153,442     | 160              | 129           | 1               | 24          |
| Internet-Stars        | 7,350.28         | 5,839.96      | 114.25          | 1,203.03    | 1,534,964        | 1,199,951     | 30,568          | 257,487     | 99               | 77            | 1               | 14          |

