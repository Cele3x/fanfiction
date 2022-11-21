# Character Gender Queries

### Genders per Source

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			totalFemales: {$sum: '$genders.females'},
			totalMales: {$sum: '$genders.males'},
			totalIndecisives: {$sum: '$genders.indecisives'},
			ratio: {$avg: '$genders.ratio'},
		}
	}
])
```

| archive         | ratio | totalFemales | totalIndecisives | totalMales |
|:----------------|:------|:-------------|:-----------------|:-----------|
| FanFiktion      | 0.63  | 19,471,225   | 3,695,846        | 36,000,856 |
| ArchiveOfOurOwn | 0.74  | 189,421      | 40,212           | 579,925    |

### Genders per Genre

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			totalFemales: {$sum: '$genders.females'},
			totalMales: {$sum: '$genders.males'},
			totalIndecisives: {$sum: '$genders.indecisives'},
			ratio: {$avg: '$genders.ratio'},
		}
	}
])
```

| genre                    | ratio | totalFemales | totalIndecisives | totalMales |
|:-------------------------|:------|:-------------|:-----------------|:-----------|
| Crossover                | 0.64  | 773,183      | 155,201          | 1,527,588  |
| Prominente               | 0.67  | 1,000,562    | 854,395          | 2,243,567  |
| Andere Medien            | 0.58  | 3,885        | 478              | 13,609     |
| Kino- & TV-Filme         | 0.66  | 522,784      | 89,729           | 977,424    |
| Serien & Podcasts        | 0.69  | 1,698,057    | 136,927          | 3,299,728  |
| Anime & Manga            | 0.59  | 3,852,594    | 917,125          | 5,561,304  |
| Bücher                   | 0.65  | 8,670,624    | 1,067,891        | 17,791,416 |
| Computerspiele           | 0.63  | 1,916,965    | 297,749          | 3,124,967  |
| Cartoons & Comics        | 0.66  | 848,013      | 145,802          | 1,473,783  |
| Musicals                 | 0.56  | 309,169      | 51,516           | 464,281    |
| Tabletop- & Rollenspiele | 0.66  | 64,810       | 19,245           | 103,114    |

### Genders per Top Fandom for each Genre

```javascript
let genres = ['Bücher', 'Prominente', 'Anime & Manga', 'Serien & Podcasts', 'Kino- & TV-Filme', 'Crossover', 'Computerspiele', 'Cartoons & Comics', 'Musicals', 'Andere Medien', 'Tabletop- & Rollenspiele']
let topFandoms = {
	'Bücher': 'Harry Potter',
	'Prominente': 'Musik',
	'Anime & Manga': 'Naruto',
	'Serien & Podcasts': 'Supernatural',
	'Kino- & TV-Filme': 'Marvel',
	'Crossover': 'Crossover',
	'Computerspiele': 'Onlinespiele',
	'Cartoons & Comics': 'Marvel',
	'Musicals': 'Tanz der Vampire',
	'Andere Medien': 'Kanon',
	'Tabletop- & Rollenspiele': 'Das Schwarze Auge'
}

db.stories.aggregate([
	{
		$match: {
			'fandoms.tier1': topFandoms[genres[0]],
			'genre': genres[0]
		}
	},
	{
		$group: {
			_id: null,
			total_females: {$sum: '$genders.females'},
			total_males: {$sum: '$genders.males'},
			total_indecisives: {$sum: '$genders.indecisives'},
			ratio: {$avg: '$genders.ratio'},
		}
	}
])
```

| genre                    | totaleFemales | totalMales | totalIndecisives | ratio |
|:-------------------------|:--------------|:-----------|:-----------------|:------|
| Bücher                   | 5,610,389     | 13,296,037 | 720,302          | 0.69  |
| Prominente               | 379,515       | 978,215    | 115,466          | 0.66  |
| Anime & Manga            | 393,172       | 571,593    | 109,423          | 0.57  |
| Serien & Podcasts        | 52,332        | 294,194    | 7,557            | 0.89  |
| Kino- & TV-Filme         | 107,142       | 318,954    | 11,002           | 0.77  |
| Crossover                | 506,279       | 1,068,512  | 87,774           | 0.64  |
| Computerspiele           | 266,543       | 365,981    | 37,953           | 0.58  |
| Cartoons & Comics        | 5,157         | 45,670     | 1,520            | 0.87  |
| Musicals                 | 94,481        | 207,777    | 9,398            | 0.64  |
| Andere Medien            | 3,308         | 12,146     | 439              | 0.58  |
| Tabletop- & Rollenspiele | 16,806        | 19,672     | 3,997            | 0.63  |

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

| fandom                | avgNumCharacters | avgNumLetters | avgNumSentences | avgNumWords | maxNumCharacters | maxNumLetters | maxNumSentences | maxNumWords | minNumCharacters | minNumLetters | minNumSentences | minNumWords |
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
				quantity: {$sum: 1}
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
		$group: {
			_id: '$fandoms',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			fandom: '$_id.name',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalStoryFandoms]}, 100]}, 2]}
		}
	},
	{
		$sort: {frequency: -1}
	},
	{
		$limit: 20
	}
])
```

| fandom                                           | frequency | percent |
|:-------------------------------------------------|:----------|:--------|
| Harry Potter - Harry Potter                      | 55,628    | 13.35   |
| Naruto - Naruto FFs                              | 26,502    | 6.36    |
| Internet-Stars - YouTuber                        | 17,750    | 4.26    |
| Bis\(s\)                                         | 13,779    | 3.31    |
| One Piece                                        | 11,532    | 2.77    |
| Sport - Fußball - Männerfußball                  | 7,860     | 1.89    |
| Supernatural                                     | 6,551     | 1.57    |
| Musik - One Direction                            | 6,079     | 1.46    |
| J.R.R. Tolkien - Mittelerde - Der Herr der Ringe | 4,894     | 1.17    |
| Sherlock BBC                                     | 4,777     | 1.15    |
| Navy CIS - Navy CIS                              | 4,406     | 1.06    |
| Die Tribute von Panem                            | 4,394     | 1.05    |
| Musik - Tokio Hotel                              | 4,219     | 1.01    |
| Rick Riordan - Rick Riordan                      | 4,011     | 0.96    |
| Crossover                                        | 3,869     | 0.93    |
| Detektiv Conan                                   | 3,862     | 0.93    |
| Yu-Gi-Oh! - Allgemein                            | 3,811     | 0.91    |
| Star Wars                                        | 3,781     | 0.91    |
| Inu Yasha - A Feudal Fairy Tale                  | 3,762     | 0.9     |
| Hetalia                                          | 3,710     | 0.89    |

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
		$unwind: {
			path: '$_id',
			preserveNullAndEmptyArrays: true
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
		$sort: {frequency: -1}
	},
	{
		$limit: 20
	}
])
```

| fandom                | frequency | percent |
|:----------------------|:----------|:--------|
| Harry Potter          | 56,038    | 13.57   |
| Musik                 | 38,917    | 9.42    |
| Naruto                | 27,487    | 6.66    |
| Internet-Stars        | 17,843    | 4.32    |
| Bis\(s\)              | 13,772    | 3.34    |
| Sport                 | 12,007    | 2.91    |
| One Piece             | 11,521    | 2.79    |
| J.R.R. Tolkien        | 8,476     | 2.05    |
| Supernatural          | 6,515     | 1.58    |
| Marvel                | 5,622     | 1.36    |
| Yu-Gi-Oh!             | 5,304     | 1.28    |
| Navy CIS              | 4,711     | 1.14    |
| Sherlock BBC          | 4,656     | 1.13    |
| Die Tribute von Panem | 4,391     | 1.06    |
| Rick Riordan          | 4,060     | 0.98    |
| Schauspieler          | 4,010     | 0.97    |
| Detektiv Conan        | 3,932     | 0.95    |
| Star Wars             | 3,916     | 0.95    |
| Crossover             | 3,867     | 0.94    |
| Inu Yasha             | 3,792     | 0.92    |

### Genre Frequencies

```javascript
let totalStories = db.stories.countDocuments({})

db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalStories]}, 100]}, 2]}
		}
	},
	{
		$sort: {frequency: -1}
	}
])
```

| frequency | genre                    | percent |
|:----------|:-------------------------|:--------|
| 111,067   | Bücher                   | 26.9    |
| 108,616   | Anime & Manga            | 26.3    |
| 77,568    | Prominente               | 18.79   |
| 58,128    | Serien & Podcasts        | 14.08   |
| 19,889    | Kino- & TV-Filme         | 4.82    |
| 17,462    | Computerspiele           | 4.23    |
| 10,330    | Cartoons & Comics        | 2.5     |
| 5,414     | Crossover                | 1.31    |
| 2,795     | Musicals                 | 0.68    |
| 886       | Andere Medien            | 0.21    |
| 768       | Tabletop- & Rollenspiele | 0.19    |

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
		$group: {
			_id: {fandom: '$fandoms.tier1', genre: '$genre'},
			quantity: {$sum: 1}
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
		$sort: {frequency: -1}
	}
])
```

| fandom            | frequency | genre                    |
|:------------------|:----------|:-------------------------|
| Harry Potter      | 56,191    | Bücher                   |
| Musik             | 39,214    | Prominente               |
| Naruto            | 27,501    | Anime & Manga            |
| Supernatural      | 6,530     | Serien & Podcasts        |
| Marvel            | 5,314     | Kino- & TV-Filme         |
| Crossover         | 3,868     | Crossover                |
| Onlinespiele      | 2,842     | Computerspiele           |
| Marvel            | 1,166     | Cartoons & Comics        |
| Tanz der Vampire  | 794       | Musicals                 |
| Kanon             | 628       | Andere Medien            |
| Das Schwarze Auge | 185       | Tabletop- & Rollenspiele |

### Genre Share per Source

```javascript
let genres = ['Bücher', 'Prominente', 'Anime & Manga', 'Serien & Podcasts', 'Kino- & TV-Filme', 'Crossover', 'Computerspiele', 'Cartoons & Comics', 'Musicals', 'Andere Medien', 'Tabletop- & Rollenspiele']
let totalStoriesFF = db.stories.countDocuments({source: 'FanFiktion'})
let totalStoriesAO3 = db.stories.countDocuments({source: 'ArchiveOfOurOwn'})

db.stories.aggregate([
	{
		$match: {
			'genre': genres[0]
		}
	},
	{
		$group: {
			_id: '$source',
			count: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			source: '$_id',
			count: 1,
			percent: {$round: [{$multiply: [{$divide: ['$count', {$cond: {if: {$eq: ['$_id', 'FanFiktion']}, then: totalStoriesFF, else: totalStoriesAO3}}]}, 100]}, 2]}
		}
	}
])
```
| genre                    | archive         | count  | percent |
|:-------------------------|:----------------|:-------|:--------|
| Bücher                   | ArchiveOfOurOwn | 5060   | 27.99   |
| Bücher                   | FanFiktion      | 106007 | 26.85   |
| Prominente               | ArchiveOfOurOwn | 1714   | 9.48    |
| Prominente               | FanFiktion      | 75854  | 19.21   |
| Anime & Manga            | ArchiveOfOurOwn | 1571   | 8.69    |
| Anime & Manga            | FanFiktion      | 107045 | 27.11   |
| Serien & Podcasts        | FanFiktion      | 51942  | 13.15   |
| Serien & Podcasts        | ArchiveOfOurOwn | 6186   | 34.22   |
| Kino- & TV-Filme         | FanFiktion      | 19093  | 4.84    |
| Kino- & TV-Filme         | ArchiveOfOurOwn | 796    | 4.4     |
| Crossover                | FanFiktion      | 5414   | 1.37    |
| Computerspiele           | FanFiktion      | 16923  | 4.29    |
| Computerspiele           | ArchiveOfOurOwn | 539    | 2.98    |
| Cartoons & Comics        | ArchiveOfOurOwn | 1266   | 7       |
| Cartoons & Comics        | FanFiktion      | 9064   | 2.3     |
| Musicals                 | FanFiktion      | 2738   | 0.69    |
| Musicals                 | ArchiveOfOurOwn | 57     | 0.32    |
| Andere Medien            | ArchiveOfOurOwn | 886    | 4.9     |
| Tabletop- & Rollenspiele | FanFiktion      | 768    | 0.19    |

### Top Fandoms on FanFiktion.de per Genre

```javascript
let totalStoriesFF = db.stories.countDocuments({source: 'FanFiktion'})

db.stories.aggregate([
	{
		$match: {
			source: 'FanFiktion'
		}
	},
	{
		$group: {
			_id: '$fandoms.tier1',
			count: {$sum: 1}
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
			percent: {$round: [{$multiply: [{$divide: ['$count', totalStoriesFF]}, 100]}, 2]}
		}
	},
	{
		$sort: {count: -1}
	},
	{
		$limit: 20
	}
])
```

| count  | fandom                | percent |
|:-------|:----------------------|:--------|
| 54,405 | Harry Potter          | 13.78   |
| 38,568 | Musik                 | 9.77    |
| 27,303 | Naruto                | 6.91    |
| 17,830 | Internet-Stars        | 4.52    |
| 13,734 | Bis\(s\)              | 3.48    |
| 11,443 | One Piece             | 2.9     |
| 11,440 | Sport                 | 2.9     |
| 8,199  | J.R.R. Tolkien        | 2.08    |
| 6,045  | Supernatural          | 1.53    |
| 5,311  | Marvel                | 1.35    |
| 5,185  | Yu-Gi-Oh!             | 1.31    |
| 4,676  | Navy CIS              | 1.18    |
| 4,372  | Die Tribute von Panem | 1.11    |
| 4,284  | Sherlock BBC          | 1.08    |
| 4,044  | Rick Riordan          | 1.02    |
| 3,907  | Schauspieler          | 0.99    |
| 3,892  | Detektiv Conan        | 0.99    |
| 3,867  | Crossover             | 0.98    |
| 3,784  | Inu Yasha             | 0.96    |
| 3,756  | Star Wars             | 0.95    |

### Top Fandoms on ArchiveOfOurOwn per Genre

```javascript
let totalStoriesAO3 = db.stories.countDocuments({source: 'ArchiveOfOurOwn'})

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
			count: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			fandom: '$_id',
			count: 1,
			percent: {$round: [{$multiply: [{$divide: ['$count', totalStoriesAO3]}, 100]}, 2]}
		}
	},
	{
		$sort: {count: -1}
	},
	{
		$limit: 20
	}
])
```

| count | fandom                                 | percent |
|:------|:---------------------------------------|:--------|
| 2,978 | Tatort                                 | 16.48   |
| 1,793 | Harry Potter                           | 9.92    |
| 1,234 | Marvel                                 | 6.83    |
| 671   | Kanon                                  | 3.71    |
| 663   | Sport                                  | 3.67    |
| 654   | Musik                                  | 3.62    |
| 509   | The Three Investigators - Die drei ??? | 2.82    |
| 506   | Supernatural                           | 2.8     |
| 493   | Sherlock BBC                           | 2.73    |
| 487   | J.R.R. Tolkien                         | 2.69    |
| 462   | Stargate                               | 2.56    |
| 416   | Polizeiruf 110                         | 2.3     |
| 368   | Star Trek                              | 2.04    |
| 349   | Star Wars                              | 1.93    |
| 291   | DC                                     | 1.61    |
| 208   | Historical RPF                         | 1.15    |
| 200   | Naruto                                 | 1.11    |
| 196   | Teen Wolf                              | 1.08    |
| 178   | Buffy & Angel                          | 0.98    |
| 174   | Glee                                   | 0.96    |

# General Statistics Queries

### Scraping Time Period

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			minCreatedAt: {$min: "$createdAt"},
			maxCreatedAt: {$max: "$createdAt"},
			minUpdatedAt: {$min: "$updatedAt"},
			maxUpdatedAt: {$max: "$updatedAt"}
		}
	},
])
```

| archive         | maxCreatedAt             | maxUpdatedAt             | minCreatedAt             | minUpdatedAt             |
|:----------------|:-------------------------|:-------------------------|:-------------------------|:-------------------------|
| FanFiktion      | 2022-08-23T08:58:55.600Z | 2022-08-23T11:51:34.930Z | 2022-01-28T15:03:34.827Z | 2022-01-31T09:21:16.908Z |
| ArchiveOfOurOwn | 2022-08-08T10:13:03.154Z | 2022-08-08T10:13:03.154Z | 2022-07-25T16:29:34.428Z | 2022-07-25T16:29:34.428Z |

### Stories per Source

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			storyCount: {$sum: 1}
		}
	}
])
```

| archive         | storyCount |
|:----------------|:-----------|
| FanFiktion      | 394,848    |
| ArchiveOfOurOwn | 18,075     |

### Chapters per Source

```javascript
db.chapters.aggregate([
	{
		$group: {
			_id: '$source',
			storyCount: {$sum: 1}
		}
	}
])
```

| archive         | storyCount |
|:----------------|:-----------|
| ArchiveOfOurOwn | 70,857     |
| FanFiktion      | 1,885,066  |

### Users per Source

```javascript
db.users.aggregate([
	{
		$group: {
			_id: '$source',
			userCount: {$sum: 1}
		}
	}
])
```

| archive         | userCount |
|:----------------|:----------|
| FanFiktion      | 135,726   |
| ArchiveOfOurOwn | 14,249    |

### Reviews per Source

```javascript
db.reviews.aggregate([
	{
		$group: {
			_id: '$source',
			reviewCount: {$sum: 1}
		}
	}
])
```

| archive         | reviewCount |
|:----------------|:------------|
| FanFiktion      | 4,849,646   |
| ArchiveOfOurOwn | 37,721      |

# Pronoun Queries

### Gender Representation per Pronoun Usage

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			prnEr: {$sum: '$pronouns.er'},
			prnIhm: {$sum: '$pronouns.ihm'},
			prnIhn: {$sum: '$pronouns.ihn'},
			prnIhr: {$sum: '$pronouns.ihr'},
			prnIhrer: {$sum: '$pronouns.ihrer'},
			prnSeiner: {$sum: '$pronouns.seiner'},
			prnSie: {$sum: '$pronouns.sie'}
		}
	},
	{
		$project: {
			_id: 1,
			prnMale: {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnSeiner']},
			prnFemale: {$sum: ['$prnIhr', '$prnIhrer', '$prnSie']},
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			prnMalePercent: {$round: [{$multiply: [{$divide: ['$prnMale', {$sum: ['$prnMale', '$prnFemale']}]}, 100]}, 2]},
			prnFemalePercent: {$round: [{$multiply: [{$divide: ['$prnFemale', {$sum: ['$prnMale', '$prnFemale']}]}, 100]}, 2]},
			total: {$sum: ['$prnMale', '$prnFemale']}
		}
	},
	{
		$sort: {total: -1}
	}
])
```

| genre                    | prnFemalePercent | prnMalePercent | total      |
|:-------------------------|:-----------------|:---------------|:-----------|
| Bücher                   | 38.05            | 61.95          | 64,144,827 |
| Serien & Podcasts        | 35.96            | 64.04          | 27,431,159 |
| Anime & Manga            | 33.55            | 66.45          | 18,979,393 |
| Kino- & TV-Filme         | 37.65            | 62.35          | 8,948,841  |
| Computerspiele           | 37.66            | 62.34          | 8,765,844  |
| Prominente               | 20.71            | 79.29          | 6,469,078  |
| Cartoons & Comics        | 39.08            | 60.92          | 4,500,338  |
| Crossover                | 36.86            | 63.14          | 2,640,782  |
| Musicals                 | 38.2             | 61.8           | 1,564,273  |
| Tabletop- & Rollenspiele | 41.39            | 58.61          | 347,633    |
| Andere Medien            | 25.94            | 74.06          | 282,224    |

### Gender Representation per Pronoun Usage and Genre

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			prnEr: {$sum: '$pronouns.er'},
			prnIhm: {$sum: '$pronouns.ihm'},
			prnIhn: {$sum: '$pronouns.ihn'},
			prnIhr: {$sum: '$pronouns.ihr'},
			prnIhrer: {$sum: '$pronouns.ihrer'},
			prnSeiner: {$sum: '$pronouns.seiner'},
			prnSie: {$sum: '$pronouns.sie'}
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			prnErPercent: {$round: [{$multiply: [{$divide: ['$prnEr', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			prnIhmPercent: {$round: [{$multiply: [{$divide: ['$prnIhm', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			prnIhnPercent: {$round: [{$multiply: [{$divide: ['$prnIhn', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			prnIhrPercent: {$round: [{$multiply: [{$divide: ['$prnIhr', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			prnIhrerPercent: {$round: [{$multiply: [{$divide: ['$prnIhrer', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			prnSeinerPercent: {$round: [{$multiply: [{$divide: ['$prnSeiner', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			prnSiePercent: {$round: [{$multiply: [{$divide: ['$prnSie', {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			total: {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}
		}
	}
])
```

| genre                    | prnErPercent | prnIhmPercent | prnIhnPercent | prnIhrPercent | prnIhrerPercent | prnSeinerPercent | prnSiePercent | total      |
|:-------------------------|:-------------|:--------------|:--------------|:--------------|:----------------|:-----------------|:--------------|:-----------|
| Crossover                | 43.8         | 8.93          | 10.4          | 7.7           | 0               | 0                | 29.15         | 2,640,782  |
| Prominente               | 54.01        | 12.07         | 13.21         | 4.44          | 0               | 0                | 16.27         | 6,469,078  |
| Andere Medien            | 51.41        | 10.88         | 11.77         | 4.8           | 0.01            | 0.01             | 21.13         | 282,224    |
| Kino- & TV-Filme         | 42.94        | 9.23          | 10.18         | 7.55          | 0.01            | 0                | 30.09         | 8,948,841  |
| Serien & Podcasts        | 44.04        | 9.57          | 10.43         | 7.02          | 0               | 0                | 28.94         | 27,431,159 |
| Anime & Manga            | 45.78        | 9.94          | 10.72         | 6.88          | 0               | 0                | 26.66         | 18,979,393 |
| Bücher                   | 42.88        | 8.97          | 10.1          | 7.49          | 0.01            | 0                | 30.55         | 64,144,827 |
| Computerspiele           | 42.77        | 9.31          | 10.25         | 7.56          | 0.01            | 0                | 30.09         | 8,765,844  |
| Cartoons & Comics        | 41.92        | 8.89          | 10.1          | 7.88          | 0.01            | 0                | 31.2          | 4,500,338  |
| Musicals                 | 42.85        | 9.11          | 9.85          | 7.21          | 0.01            | 0                | 30.98         | 1,564,273  |
| Tabletop- & Rollenspiele | 40.3         | 8.74          | 9.56          | 8.11          | 0.01            | 0                | 33.27         | 347,633    |

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
|:----------|:--------|:--------|
| 276,188   | Generic | 66.5    |
| 117,051   | M/M     | 28.18   |
| 14,784    | F/M     | 3.56    |
| 2,826     | F/F     | 0.68    |
| 2,702     | Multi   | 0.65    |
| 1,059     | null    | 0.25    |
| 693       | Other   | 0.17    |

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

| frequency | percent | rating    |
|:----------|:--------|:----------|
| 188,704   | 45.7    | P12       |
| 118,480   | 28.69   | P16       |
| 67,995    | 16.47   | P18       |
| 33,654    | 8.15    | P6        |
| 2,223     | 0.54    | P18-AVL   |
| 1,867     | 0.45    | Not Rated |

# User Gender Queries

### User Genders for FanFiktion.de

```javascript
let totalUsersFF = db.users.countDocuments({source: 'FanFiktion'})

db.users.aggregate([
	{
		$match: {
			source: 'FanFiktion'
		}
	},
	{
		$group: {
			_id: '$gender',
			quantity: {$sum: 1},
			age: {$avg: '$age'}
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', totalUsersFF]}, 100]}, 2]},
			avgAge: '$age'
		}
	}
])
```

| avgAge             | frequency | genre  | percent |
|:-------------------|:----------|:-------|:--------|
| 23.115023474178404 | 671       | other  | 0.49    |
| 26889510870704658  | 87,784    | female | 64.68   |
| 27.10342481288274  | 39,437    | null   | 29.06   |
| 27.9820692497939   | 7,834     | male   | 5.77    |

### Story Author Genders for FanFiktion.de

```javascript
let uniqueAuthorsFF = db.stories.distinct('authorId', {source: 'FanFiktion'}).length

db.stories.aggregate([
	{
		$match: {source: 'FanFiktion'}
	},
	{
		$lookup: {
			from: 'users',
			localField: 'authorId',
			foreignField: '_id',
			as: 'author'
		}
	},
	{
		$unwind: '$author'
	},
	{
		$group: {
			_id: '$author'
		}
	},
	{
		$group: {
			_id: '$_id.gender',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			gender: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', uniqueAuthorsFF]}, 100]}, 2]},
		}
	}
])
```

| frequency | gender | percent |
|:----------|:-------|:--------|
| 6,291     | male   | 5.87    |
| 72,959    | female | 68.04   |
| 511       | other  | 0.48    |
| 27,463    | null   | 25.61   |

### Review Author Genders for FanFiktion.de

```javascript
let uniqueReviewersFF = db.reviews.distinct('userId', {source: 'FanFiktion'}).length

db.reviews.aggregate([
	{
		$match: {source: 'FanFiktion'}
	},
	{
		$lookup: {
			from: 'users',
			localField: 'userId',
			foreignField: '_id',
			as: 'author'
		}
	},
	{
		$unwind: '$author'
	},
	{
		$group: {
			_id: '$author'
		}
	},
	{
		$group: {
			_id: '$_id.gender',
			quantity: {$sum: 1}
		}
	},
	{
		$project: {
			_id: 0,
			gender: '$_id',
			frequency: '$quantity',
			percent: {$round: [{$multiply: [{$divide: ['$quantity', uniqueReviewersFF]}, 100]}, 2]},
		}
	}
])
```

| frequency | gender | percent |
|:----------|:-------|:--------|
| 51,084    | female | 67.89   |
| 19,185    | null   | 25.5    |
| 4,521     | male   | 6.01    |
| 450       | other  | 0.6     |

### Male/Female Characters and Pronouns Usage in Relation to Authors Sex

```javascript
db.stories.aggregate([
	{
		$lookup: {
			from: 'users',
			localField: 'authorId',
			foreignField: '_id',
			as: 'author'
		}
	},
	{
		$unwind: '$author'
	},
	{
		$group: {
			_id: '$author.gender',
			sumFemaleChars: {$sum: '$genders.females'},
			sumMaleChars: {$sum: '$genders.males'},
			prnEr: {$sum: '$pronouns.er'},
			prnIhm: {$sum: '$pronouns.ihm'},
			prnIhn: {$sum: '$pronouns.ihn'},
			prnIhr: {$sum: '$pronouns.ihr'},
			prnIhrer: {$sum: '$pronouns.ihrer'},
			prnSeiner: {$sum: '$pronouns.seiner'},
			prnSie: {$sum: '$pronouns.sie'}
		}
	},
	{
		$project: {
			_id: 0,
			authorGender: '$_id',
			femaleCharsPercent: {$round: [{$multiply: [{$divide: ['$sumFemaleChars', {$sum: ['$sumFemaleChars', '$sumMaleChars']}]}, 100]}, 2]},
			maleCharsPercent: {$round: [{$multiply: [{$divide: ['$sumMaleChars', {$sum: ['$sumFemaleChars', '$sumMaleChars']}]}, 100]}, 2]},
			femalePronounsPercent: {$round: [{$multiply: [{$divide: [{$sum: ['$prnIhr', '$prnIhrer', '$prnSie']}, {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			malePronounsPercent: {$round: [{$multiply: [{$divide: [{$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnSeiner']}, {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]}
		}
	}
])
```

| authorGender | femaleCharsPercent | femalePronounsPercent | maleCharsPercent | malePronounsPercent |
|:-------------|:-------------------|:----------------------|:-----------------|:--------------------|
| other        | 31.03              | 31.69                 | 68.97            | 68.31               |
| null         | 31.85              | 31.82                 | 68.15            | 68.18               |
| male         | 34.52              | 35.64                 | 65.48            | 64.36               |
| female       | 35.82              | 37.66                 | 64.18            | 62.34               |

### Male/Female Characters and Pronouns Usage in Relation to Authors Age

```javascript
db.stories.aggregate([
	{
		$lookup: {
			from: 'users',
			localField: 'authorId',
			foreignField: '_id',
			as: 'author'
		}
	},
	{
		$unwind: '$author'
	},
	{
		$match: {
			'author.age': {$ne: null, $gt: 0}
		}
	},
	{
		$group: {
			_id: {
				$cond: [
					{$lte: ['$author.age', 20]},
					'1-20',
					{
						$cond: [
							{$lte: ['$author.age', 25]},
							'21-25',
							{
								$cond: [
									{$lte: ['$author.age', 30]},
									'26-30',
									'31+'
								]
							}
						]
					}
				]
			},
			count: {$sum: 1},
			sumFemaleChars: {$sum: '$genders.females'},
			sumMaleChars: {$sum: '$genders.males'},
			prnEr: {$sum: '$pronouns.er'},
			prnIhm: {$sum: '$pronouns.ihm'},
			prnIhn: {$sum: '$pronouns.ihn'},
			prnIhr: {$sum: '$pronouns.ihr'},
			prnIhrer: {$sum: '$pronouns.ihrer'},
			prnSeiner: {$sum: '$pronouns.seiner'},
			prnSie: {$sum: '$pronouns.sie'}
		}
	},
	{
		$project: {
			_id: 0,
			count: 1,
			authorAge: '$_id',
			femaleCharsPercent: {$round: [{$multiply: [{$divide: ['$sumFemaleChars', {$sum: ['$sumFemaleChars', '$sumMaleChars']}]}, 100]}, 2]},
			maleCharsPercent: {$round: [{$multiply: [{$divide: ['$sumMaleChars', {$sum: ['$sumFemaleChars', '$sumMaleChars']}]}, 100]}, 2]},
			femalePronounsPercent: {$round: [{$multiply: [{$divide: [{$sum: ['$prnIhr', '$prnIhrer', '$prnSie']}, {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
			malePronounsPercent: {$round: [{$multiply: [{$divide: [{$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnSeiner']}, {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']}]}, 100]}, 2]},
		}
	}
])
```

| authorAge | count  | femaleCharsPercent | femalePronounsPercent | maleCharsPercent | malePronounsPercent |
|:----------|:-------|:-------------------|:----------------------|:-----------------|:--------------------|
| 1-20      | 15,380 | 39.18              | 41.9                  | 60.82            | 58.1                |
| 21-25     | 70,171 | 38.51              | 38.93                 | 61.49            | 61.07               |
| 26-30     | 64,502 | 37.14              | 38.69                 | 62.86            | 61.31               |
| 31+       | 56,684 | 33.42              | 35.18                 | 66.58            | 64.82               |

### Male/Female Characters, Pronouns and Pairings Usage in Relation to Authors Age

```javascript
db.stories.aggregate([
	{
		$lookup: {
			from: 'users',
			localField: 'authorId',
			foreignField: '_id',
			as: 'author'
		}
	},
	{
		$unwind: '$author'
	},
	{
		$unwind: {
			path: '$pairings',
			preserveNullAndEmptyArrays: true
		}
	},
	{
		$match: {
			'author.age': {$ne: null, $gt: 0}
		}
	},
	{
		$group: {
			_id: {
				$cond: [
					{$lte: ['$author.age', 20]},
					'1-20',
					{
						$cond: [
							{$lte: ['$author.age', 25]},
							'21-25',
							{
								$cond: [
									{$lte: ['$author.age', 30]},
									'26-30',
									'31+'
								]
							}
						]
					}
				]
			},
			count: {$sum: 1},
			sumFemaleChars: {$sum: '$genders.females'},
			sumMaleChars: {$sum: '$genders.males'},
			prnEr: {$sum: '$pronouns.er'},
			prnIhm: {$sum: '$pronouns.ihm'},
			prnIhn: {$sum: '$pronouns.ihn'},
			prnIhr: {$sum: '$pronouns.ihr'},
			prnIhrer: {$sum: '$pronouns.ihrer'},
			prnSeiner: {$sum: '$pronouns.seiner'},
			prnSie: {$sum: '$pronouns.sie'},
			sumPairingsMM: {$sum: {$cond: [{$eq: ['$pairings', 'M/M']}, 1, 0]}},
			sumPairingsFM: {$sum: {$cond: [{$eq: ['$pairings', 'F/M']}, 1, 0]}},
			sumPairingsFF: {$sum: {$cond: [{$eq: ['$pairings', 'F/F']}, 1, 0]}},
			sumPairingsMulti: {$sum: {$cond: [{$eq: ['$pairings', 'Multi']}, 1, 0]}},
			sumPairingsGeneric: {$sum: {$cond: [{$eq: ['$pairings', 'Generic']}, 1, 0]}},
			sumPairingsOther: {$sum: {$cond: [{$eq: ['$pairings', 'Other']}, 1, 0]}}
		}
	},
	{
		$project: {
			_id: 0,
			ageGroup: '$_id',
			count: 1,
			femaleChars: '$sumFemaleChars',
			maleChars: '$sumMaleChars',
			totalChars: {$sum: ['$sumFemaleChars', '$sumMaleChars']},
			femalePronouns: {$sum: ['$prnIhr', '$prnIhrer', '$prnSie']},
			malePronouns: {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnSeiner']},
			totalPronouns: {$sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie']},
			sumPairingsMM: 1,
			sumPairingsFM: 1,
			sumPairingsFF: 1,
			sumPairingsMulti: 1,
			sumPairingsGeneric: 1,
			sumPairingsOther: 1,
			totalPairings: {$sum: ['$sumPairingsMM', '$sumPairingsFM', '$sumPairingsFF', '$sumPairingsMulti', '$sumPairingsGeneric', '$sumPairingsOther']},
		}
	},
	{
		$project: {
			_id: 0,
			ageGroup: 1,
			charsRatio: {$round: [{$divide: ['$maleChars', '$totalChars']}, 2]},
			pronounsRatio: {$round: [{$divide: ['$malePronouns', '$totalPronouns']}, 2]},
			pairingsMMPercent: {$round: [{$multiply: [{$divide: ['$sumPairingsMM', '$totalPairings']}, 100]}, 2]},
			pairingsFMPercent: {$round: [{$multiply: [{$divide: ['$sumPairingsFM', '$totalPairings']}, 100]}, 2]},
			pairingsFFPercent: {$round: [{$multiply: [{$divide: ['$sumPairingsFF', '$totalPairings']}, 100]}, 2]},
			pairingsMultiPercent: {$round: [{$multiply: [{$divide: ['$sumPairingsMulti', '$totalPairings']}, 100]}, 2]},
			pairingsGenericPercent: {$round: [{$multiply: [{$divide: ['$sumPairingsGeneric', '$totalPairings']}, 100]}, 2]},
			pairingsOtherPercent: {$round: [{$multiply: [{$divide: ['$sumPairingsOther', '$totalPairings']}, 100]}, 2]},
		}
	}
])
```

| ageGroup | charsRatio | pairingsFFPercent | pairingsFMPercent | pairingsGenericPercent | pairingsMMPercent | pairingsMultiPercent | pairingsOtherPercent | pronounsRatio |
|:---------|:-----------|:------------------|:------------------|:-----------------------|:------------------|:---------------------|:---------------------|:--------------|
| 1-20     | 0.61       | 0.62              | 5.2               | 73.52                  | 19.07             | 1.41                 | 0.18                 | 0.58          |
| 31+      | 0.67       | 0.57              | 3.25              | 64.25                  | 31.52             | 0.35                 | 0.07                 | 0.65          |
| 26-30    | 0.63       | 0.57              | 2.56              | 67.96                  | 28.43             | 0.44                 | 0.04                 | 0.61          |
| 21-25    | 0.61       | 0.28              | 2.95              | 71.95                  | 24.12             | 0.62                 | 0.08                 | 0.61          |

### User Sex Distribution per Genre

```javascript
db.stories.aggregate([
	{
		$match: {source: 'FanFiktion'}
	},
	{
		$lookup: {
			from: 'users',
			localField: 'authorId',
			foreignField: '_id',
			as: 'author'
		}
	},
	{
		$unwind: '$author'
	},
	{
		$group: {
			_id: '$genre',
			count: {$sum: 1},
			femaleAuthors: {$sum: {$cond: [{$eq: ['$author.gender', 'female']}, 1, 0]}},
			maleAuthors: {$sum: {$cond: [{$eq: ['$author.gender', 'male']}, 1, 0]}},
			otherAuthors: {$sum: {$cond: [{$eq: ['$author.gender', 'other']}, 1, 0]}},
			nullAuthors: {$sum: {$cond: [{$eq: ['$author.gender', 'female']}, 0, {$cond: [{$eq: ['$author.gender', 'male']}, 0, {$cond: [{$eq: ['$author.gender', 'other']}, 0, 1]}]}]}}
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			count: 1,
			femaleAuthors: 1,
			femaleAuthorPercent: {$round: [{$multiply: [{$divide: ['$femaleAuthors', '$count']}, 100]}, 2]},
			maleAuthors: 1,
			maleAuthorPercent: {$round: [{$multiply: [{$divide: ['$maleAuthors', '$count']}, 100]}, 2]},
			otherAuthors: 1,
			otherAuthorPercent: {$round: [{$multiply: [{$divide: ['$otherAuthors', '$count']}, 100]}, 2]},
			nullAuthors: 1,
			nullAuthorPercent: {$round: [{$multiply: [{$divide: ['$nullAuthors', '$count']}, 100]}, 2]},
		}
	},
	{
		$sort: {count: -1}
	}
])
```

| count   | femaleAuthorPercent | femaleAuthors | genre                    | maleAuthorPercent | maleAuthors | nullAuthorPercent | nullAuthors | otherAuthorPercent | otherAuthors |
|:--------|:--------------------|:--------------|:-------------------------|:------------------|:------------|:------------------|:------------|:-------------------|:-------------|
| 107,045 | 76.2                | 81,571        | Anime & Manga            | 6.09              | 6,516       | 16.9              | 18,089      | 0.81               | 869          |
| 106,007 | 75.3                | 79,826        | Bücher                   | 4.54              | 4,810       | 19.39             | 20,559      | 0.77               | 812          |
| 75,854  | 76.34               | 57,907        | Prominente               | 2.65              | 2,012       | 20.17             | 15,296      | 0.84               | 639          |
| 51,942  | 75.67               | 39,302        | Serien & Podcasts        | 3.07              | 1,596       | 20.41             | 10,602      | 0.85               | 442          |
| 19,093  | 70.03               | 13,371        | Kino- & TV-Filme         | 8                 | 1,527       | 20.67             | 3,947       | 1.3                | 248          |
| 16,923  | 65.24               | 11,041        | Computerspiele           | 14.31             | 2,421       | 19.36             | 3,276       | 1.09               | 185          |
| 9,064   | 65.72               | 5,957         | Cartoons & Comics        | 12.41             | 1,125       | 20.53             | 1,861       | 1.33               | 121          |
| 5,414   | 63.96               | 3,463         | Crossover                | 13.32             | 721         | 21.72             | 1,176       | 1                  | 54           |
| 2,738   | 76.52               | 2,095         | Musicals                 | 3.1               | 85          | 17.35             | 475         | 3.03               | 83           |
| 768     | 30.21               | 232           | Tabletop- & Rollenspiele | 40.76             | 313         | 28.78             | 221         | 0.26               | 2            |

