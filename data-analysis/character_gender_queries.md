# Character Gender Queries

### Genders per Source
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			totalFemales: { $sum: '$genders.females' },
			totalMales: { $sum: '$genders.males' },
			totalIndecisives: { $sum: '$genders.indecisives' },
			ratio: { $avg: '$genders.ratio' },
		}
	}
])
```

### Genders per Genre
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$genre',
			totalFemales: { $sum: '$genders.females' },
			totalMales: { $sum: '$genders.males' },
			totalIndecisives: { $sum: '$genders.indecisives' },
			ratio: { $avg: '$genders.ratio' },
		}
	}
])
```

### Genders per Top Fandom for each Genre
```javascript
let genres = ['Bücher', 'Prominente', 'Anime & Manga', 'Serien & Podcasts', 'Kino- & TV-Filme', 'Crossover', 'Computerspiele', 'Cartoons & Comics', 'Musicals', 'Andere Medien', 'Tabletop- & Rollenspiele']
let topFandoms = {'Bücher': 'Harry Potter', 'Prominente': 'Musik', 'Anime & Manga': 'Naruto', 'Serien & Podcasts': 'Supernatural', 'Kino- & TV-Filme': 'Marvel', 'Crossover': 'Crossover', 'Computerspiele': 'Onlinespiele', 'Cartoons & Comics': 'Marvel', 'Musicals': 'Tanz der Vampire', 'Andere Medien': 'Kanon', 'Tabletop- & Rollenspiele': 'Das Schwarze Auge'}

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
			total_females: { $sum: '$genders.females' },
			total_males: { $sum: '$genders.males' },
			total_indecisives: { $sum: '$genders.indecisives' },
			ratio: { $avg: '$genders.ratio' },
		}
	}
])
```
