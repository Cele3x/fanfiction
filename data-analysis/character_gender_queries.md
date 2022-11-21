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
| \_id | ratio | totalFemales | totalIndecisives | totalMales |
| :--- | :--- | :--- | :--- | :--- |
| FanFiktion | 0.6285130584043107 | 19471225 | 3695846 | 36000856 |
| ArchiveOfOurOwn | 0.7353494962216625 | 189421 | 40212 | 579925 |


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
| \_id | ratio | totalFemales | totalIndecisives | totalMales |
| :--- | :--- | :--- | :--- | :--- |
| Crossover | 0.638980232772954 | 773183 | 155201 | 1527588 |
| Prominente | 0.6670885526886526 | 1000562 | 854395 | 2243567 |
| Andere Medien | 0.5768648648648649 | 3885 | 478 | 13609 |
| Kino- & TV-Filme | 0.6594509874977351 | 522784 | 89729 | 977424 |
| Serien & Podcasts | 0.6888797325662753 | 1698057 | 136927 | 3299728 |
| Anime & Manga | 0.5862640507037002 | 3852594 | 917125 | 5561304 |
| Bücher | 0.6499435483870968 | 8670624 | 1067891 | 17791416 |
| Computerspiele | 0.6251042339538434 | 1916965 | 297749 | 3124967 |
| Cartoons & Comics | 0.656042924935289 | 848013 | 145802 | 1473783 |
| Musicals | 0.5645550692924872 | 309169 | 51516 | 464281 |
| Tabletop- & Rollenspiele | 0.6516015625 | 64810 | 19245 | 103114 |


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
| genre                    | totaleFemales | totalMales | totalIndecisives | ratio |
|:-------------------------| :--- | :--- | :--- | :--- |
| Bücher                   | 5610389 | 13296037 | 720302 | 0.6858851215499908 |
| Prominente               | 379515 | 978215 | 115466 | 0.6640794681428978 |
| Anime & Manga            | 393172 | 571593 | 109423 | 0.5739952494061757 |
| Serien & Podcasts        | 52332 | 294194 | 7557 | 0.8967435359888191 |
| Kino- & TV-Filme         | 107142 | 318954 | 11002 | 0.7740978348035285 |
| Crossover                | 506279 | 1068512 | 87774 | 0.6424127230411172 |
| Computerspiele           | 266543 | 365981 | 37953 | 0.58272565742715 |
| Cartoons & Comics        | 5157 | 45670 | 1520 | 0.8648461538461538 |
| Musicals                 | 94481 | 207777 | 9398 | 0.6479150579150579 |
| Andere Medien            | 3308 | 12146 | 439 | 0.5768493150684931 |
| Tabletop- & Rollenspiele | 16806 | 19672 | 3997 | 0.6261621621621621 |