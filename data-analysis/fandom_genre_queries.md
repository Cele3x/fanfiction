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
