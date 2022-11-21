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
            fandom: '$_id.name',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryFandoms ]}, 100 ]}, 2]}
        }
    },
    {
        $sort : { frequency: -1 }
    },
	{
		$limit: 20
	}
])
```
| fandom | frequency | percent |
| :--- | :--- | :--- |
| Harry Potter - Harry Potter | 55628 | 13.35 |
| Naruto - Naruto FFs | 26502 | 6.36 |
| Internet-Stars - YouTuber | 17750 | 4.26 |
| Bis\(s\) | 13779 | 3.31 |
| One Piece | 11532 | 2.77 |
| Sport - Fußball - Männerfußball | 7860 | 1.89 |
| Supernatural | 6551 | 1.57 |
| Musik - One Direction | 6079 | 1.46 |
| J.R.R. Tolkien - Mittelerde - Der Herr der Ringe | 4894 | 1.17 |
| Sherlock BBC | 4777 | 1.15 |
| Navy CIS - Navy CIS | 4406 | 1.06 |
| Die Tribute von Panem | 4394 | 1.05 |
| Musik - Tokio Hotel | 4219 | 1.01 |
| Rick Riordan - Rick Riordan | 4011 | 0.96 |
| Crossover | 3869 | 0.93 |
| Detektiv Conan | 3862 | 0.93 |
| Yu-Gi-Oh! - Allgemein | 3811 | 0.91 |
| Star Wars | 3781 | 0.91 |
| Inu Yasha - A Feudal Fairy Tale | 3762 | 0.9 |
| Hetalia | 3710 | 0.89 |



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
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalStoryTier1Fandoms ]}, 100 ]}, 2]}
        }
    },
    {
        $sort : { frequency: -1 }
    },
	{
		$limit: 20
	}
])
```
| fandom | frequency | percent |
| :--- | :--- | :--- |
| Harry Potter | 56038 | 13.57 |
| Musik | 38917 | 9.42 |
| Naruto | 27487 | 6.66 |
| Internet-Stars | 17843 | 4.32 |
| Bis\(s\) | 13772 | 3.34 |
| Sport | 12007 | 2.91 |
| One Piece | 11521 | 2.79 |
| J.R.R. Tolkien | 8476 | 2.05 |
| Supernatural | 6515 | 1.58 |
| Marvel | 5622 | 1.36 |
| Yu-Gi-Oh! | 5304 | 1.28 |
| Navy CIS | 4711 | 1.14 |
| Sherlock BBC | 4656 | 1.13 |
| Die Tribute von Panem | 4391 | 1.06 |
| Rick Riordan | 4060 | 0.98 |
| Schauspieler | 4010 | 0.97 |
| Detektiv Conan | 3932 | 0.95 |
| Star Wars | 3916 | 0.95 |
| Crossover | 3867 | 0.94 |
| Inu Yasha | 3792 | 0.92 |


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
| frequency | genre | percent |
| :--- | :--- | :--- |
| 111067 | Bücher | 26.9 |
| 108616 | Anime & Manga | 26.3 |
| 77568 | Prominente | 18.79 |
| 58128 | Serien & Podcasts | 14.08 |
| 19889 | Kino- & TV-Filme | 4.82 |
| 17462 | Computerspiele | 4.23 |
| 10330 | Cartoons & Comics | 2.5 |
| 5414 | Crossover | 1.31 |
| 2795 | Musicals | 0.68 |
| 886 | Andere Medien | 0.21 |
| 768 | Tabletop- & Rollenspiele | 0.19 |


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
| fandom | frequency | genre |
| :--- | :--- | :--- |
| Harry Potter | 56191 | Bücher |
| Musik | 39214 | Prominente |
| Naruto | 27501 | Anime & Manga |
| Supernatural | 6530 | Serien & Podcasts |
| Marvel | 5314 | Kino- & TV-Filme |
| Crossover | 3868 | Crossover |
| Onlinespiele | 2842 | Computerspiele |
| Marvel | 1166 | Cartoons & Comics |
| Tanz der Vampire | 794 | Musicals |
| Kanon | 628 | Andere Medien |
| Das Schwarze Auge | 185 | Tabletop- & Rollenspiele |


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
	},
	{
		$limit: 20
	}
])
```
| count | fandom | percent |
| :--- | :--- | :--- |
| 54405 | Harry Potter | 13.78 |
| 38568 | Musik | 9.77 |
| 27303 | Naruto | 6.91 |
| 17830 | Internet-Stars | 4.52 |
| 13734 | Bis\(s\) | 3.48 |
| 11443 | One Piece | 2.9 |
| 11440 | Sport | 2.9 |
| 8199 | J.R.R. Tolkien | 2.08 |
| 6045 | Supernatural | 1.53 |
| 5311 | Marvel | 1.35 |
| 5185 | Yu-Gi-Oh! | 1.31 |
| 4676 | Navy CIS | 1.18 |
| 4372 | Die Tribute von Panem | 1.11 |
| 4284 | Sherlock BBC | 1.08 |
| 4044 | Rick Riordan | 1.02 |
| 3907 | Schauspieler | 0.99 |
| 3892 | Detektiv Conan | 0.99 |
| 3867 | Crossover | 0.98 |
| 3784 | Inu Yasha | 0.96 |
| 3756 | Star Wars | 0.95 |


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
	},
    {
        $limit: 20
    }
])
```
| count | fandom                                 | percent |
| :--- |:---------------------------------------| :--- |
| 2978 | Tatort                                 | 16.48 |
| 1793 | Harry Potter                           | 9.92 |
| 1234 | Marvel                                 | 6.83 |
| 671 | Kanon                                  | 3.71 |
| 663 | Sport                                  | 3.67 |
| 654 | Musik                                  | 3.62 |
| 509 | The Three Investigators - Die drei ??? | 2.82 |
| 506 | Supernatural                           | 2.8 |
| 493 | Sherlock BBC                           | 2.73 |
| 487 | J.R.R. Tolkien                         | 2.69 |
| 462 | Stargate                               | 2.56 |
| 416 | Polizeiruf 110                         | 2.3 |
| 368 | Star Trek                              | 2.04 |
| 349 | Star Wars                              | 1.93 |
| 291 | DC                                     | 1.61 |
| 208 | Historical RPF                         | 1.15 |
| 200 | Naruto                                 | 1.11 |
| 196 | Teen Wolf                              | 1.08 |
| 178 | Buffy & Angel                          | 0.98 |
| 174 | Glee                                   | 0.96 |
