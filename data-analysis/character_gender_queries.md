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

| \_id | ratio | totalFemales | totalIndecisives | totalMales |
| :--- | :--- | :--- | :--- | :--- |
| FanFiktion | 0.6,285,130,584,043,107 | 19,471,225 | 3,695,846 | 36,000,856 |
| ArchiveOfOurOwn | 0.7,353,494,962,216,625 | 189,421 | 40,212 | 579,925 |

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

| \_id | ratio | totalFemales | totalIndecisives | totalMales |
| :--- | :--- | :--- | :--- | :--- |
| Crossover | 0.638,980,232,772,954 | 773,183 | 155,201 | 1,527,588 |
| Prominente | 0.6,670,885,526,886,526 | 1,000,562 | 854,395 | 2,243,567 |
| Andere Medien | 0.5,768,648,648,648,649 | 3,885 | 478 | 13,609 |
| Kino- & TV-Filme | 0.6,594,509,874,977,351 | 522,784 | 89,729 | 977,424 |
| Serien & Podcasts | 0.6,888,797,325,662,753 | 1,698,057 | 136,927 | 3,299,728 |
| Anime & Manga | 0.5,862,640,507,037,002 | 3,852,594 | 917,125 | 5,561,304 |
| Bücher | 0.6,499,435,483,870,968 | 8,670,624 | 1,067,891 | 17,791,416 |
| Computerspiele | 0.6,251,042,339,538,434 | 1,916,965 | 297,749 | 3,124,967 |
| Cartoons & Comics | 0.656,042,924,935,289 | 848,013 | 145,802 | 1,473,783 |
| Musicals | 0.5,645,550,692,924,872 | 309,169 | 51,516 | 464,281 |
| Tabletop- & Rollenspiele | 0.6,516,015,625 | 64,810 | 19,245 | 103,114 |

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
|:-------------------------| :--- | :--- | :--- | :--- |
| Bücher                   | 5,610,389 | 13,296,037 | 720,302 | 0.6,858,851,215,499,908 |
| Prominente               | 379,515 | 978,215 | 115,466 | 0.6,640,794,681,428,978 |
| Anime & Manga            | 393,172 | 571,593 | 109,423 | 0.5,739,952,494,061,757 |
| Serien & Podcasts        | 52,332 | 294,194 | 7,557 | 0.8,967,435,359,888,191 |
| Kino- & TV-Filme         | 107,142 | 318,954 | 11,002 | 0.7,740,978,348,035,285 |
| Crossover                | 506,279 | 1,068,512 | 87,774 | 0.6,424,127,230,411,172 |
| Computerspiele           | 266,543 | 365,981 | 37,953 | 0.58,272,565,742,715 |
| Cartoons & Comics        | 5,157 | 45,670 | 1,520 | 0.8,648,461,538,461,538 |
| Musicals                 | 94,481 | 207,777 | 9,398 | 0.6,479,150,579,150,579 |
| Andere Medien            | 3,308 | 12,146 | 439 | 0.5,768,493,150,684,931 |
| Tabletop- & Rollenspiele | 16,806 | 19,672 | 3,997 | 0.6,261,621,621,621,621 |