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
