# Pronoun Queries

### Gender Representation per Pronoun Usage
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			prnEr: { $sum: '$pronouns.er' },
			prnIhm: { $sum: '$pronouns.ihm' },
			prnIhn: { $sum: '$pronouns.ihn' },
			prnIhr: { $sum: '$pronouns.ihr' },
			prnIhrer: { $sum: '$pronouns.ihrer' },
			prnSeiner: { $sum: '$pronouns.seiner' },
			prnSie: { $sum: '$pronouns.sie' }
		}
	},
	{
		$project: {
			_id: 1,
			prnMale: { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnSeiner'] },
			prnFemale: { $sum: ['$prnIhr', '$prnIhrer', '$prnSie'] },
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			prnMalePercent: { $round: [{ $multiply: [{ $divide: [ '$prnMale', { $sum: ['$prnMale', '$prnFemale'] } ]}, 100 ]}, 2]},
			prnFemalePercent: { $round: [{ $multiply: [{ $divide: [ '$prnFemale', { $sum: ['$prnMale', '$prnFemale'] } ]}, 100 ]}, 2]},
			total: { $sum: ['$prnMale', '$prnFemale'] }
		}
	},
	{
		$sort: { total: -1 }
	}
])
```
| genre | prnFemalePercent | prnMalePercent | total |
| :--- | :--- | :--- | :--- |
| Bücher | 38.05 | 61.95 | 64144827 |
| Serien & Podcasts | 35.96 | 64.04 | 27431159 |
| Anime & Manga | 33.55 | 66.45 | 18979393 |
| Kino- & TV-Filme | 37.65 | 62.35 | 8948841 |
| Computerspiele | 37.66 | 62.34 | 8765844 |
| Prominente | 20.71 | 79.29 | 6469078 |
| Cartoons & Comics | 39.08 | 60.92 | 4500338 |
| Crossover | 36.86 | 63.14 | 2640782 |
| Musicals | 38.2 | 61.8 | 1564273 |
| Tabletop- & Rollenspiele | 41.39 | 58.61 | 347633 |
| Andere Medien | 25.94 | 74.06 | 282224 |


### Gender Representation per Pronoun Usage and Genre
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			prnEr: { $sum: '$pronouns.er' },
			prnIhm: { $sum: '$pronouns.ihm' },
			prnIhn: { $sum: '$pronouns.ihn' },
			prnIhr: { $sum: '$pronouns.ihr' },
			prnIhrer: { $sum: '$pronouns.ihrer' },
			prnSeiner: { $sum: '$pronouns.seiner' },
			prnSie: { $sum: '$pronouns.sie' }
		}
	},
	{
		$project: {
			_id: 0,
			genre: '$_id',
			prnErPercent: { $round: [{ $multiply: [{ $divide: [ '$prnEr', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			prnIhmPercent: { $round: [{ $multiply: [{ $divide: [ '$prnIhm', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			prnIhnPercent: { $round: [{ $multiply: [{ $divide: [ '$prnIhn', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			prnIhrPercent: { $round: [{ $multiply: [{ $divide: [ '$prnIhr', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			prnIhrerPercent: { $round: [{ $multiply: [{ $divide: [ '$prnIhrer', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			prnSeinerPercent: { $round: [{ $multiply: [{ $divide: [ '$prnSeiner', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			prnSiePercent: { $round: [{ $multiply: [{ $divide: [ '$prnSie', { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			total: { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] }
		}
	}
])
```
| genre | prnErPercent | prnIhmPercent | prnIhnPercent | prnIhrPercent | prnIhrerPercent | prnSeinerPercent | prnSiePercent | total |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Crossover | 43.8 | 8.93 | 10.4 | 7.7 | 0 | 0 | 29.15 | 2640782 |
| Prominente | 54.01 | 12.07 | 13.21 | 4.44 | 0 | 0 | 16.27 | 6469078 |
| Andere Medien | 51.41 | 10.88 | 11.77 | 4.8 | 0.01 | 0.01 | 21.13 | 282224 |
| Kino- & TV-Filme | 42.94 | 9.23 | 10.18 | 7.55 | 0.01 | 0 | 30.09 | 8948841 |
| Serien & Podcasts | 44.04 | 9.57 | 10.43 | 7.02 | 0 | 0 | 28.94 | 27431159 |
| Anime & Manga | 45.78 | 9.94 | 10.72 | 6.88 | 0 | 0 | 26.66 | 18979393 |
| Bücher | 42.88 | 8.97 | 10.1 | 7.49 | 0.01 | 0 | 30.55 | 64144827 |
| Computerspiele | 42.77 | 9.31 | 10.25 | 7.56 | 0.01 | 0 | 30.09 | 8765844 |
| Cartoons & Comics | 41.92 | 8.89 | 10.1 | 7.88 | 0.01 | 0 | 31.2 | 4500338 |
| Musicals | 42.85 | 9.11 | 9.85 | 7.21 | 0.01 | 0 | 30.98 | 1564273 |
| Tabletop- & Rollenspiele | 40.3 | 8.74 | 9.56 | 8.11 | 0.01 | 0 | 33.27 | 347633 |

