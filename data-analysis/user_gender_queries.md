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
        $group : {
            _id: '$gender',
            quantity: { $sum: 1 },
	        age: { $avg: '$age' }
        }
    },
    {
        $project: {
            _id: 0,
            genre: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', totalUsersFF ]}, 100 ]}, 2]},
	        avgAge: '$age'
        }
    }
])
```
| avgAge | frequency | genre | percent |
| :--- | :--- | :--- | :--- |
| 23.115023474178404 | 671 | other | 0.49 |
| 26.889510870704658 | 87784 | female | 64.68 |
| 27.10342481288274 | 39437 | null | 29.06 |
| 27.9820692497939 | 7834 | male | 5.77 |


### Story Author Genders for FanFiktion.de
```javascript
let uniqueAuthorsFF = db.stories.distinct('authorId', { source: 'FanFiktion' }).length

db.stories.aggregate([
	{
		$match: { source: 'FanFiktion' }
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
			quantity: { $sum: 1 }
		}
	},
    {
        $project: {
            _id: 0,
            gender: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', uniqueAuthorsFF ]}, 100 ]}, 2]},
        }
    }
])
```
| frequency | gender | percent |
| :--- | :--- | :--- |
| 6291 | male | 5.87 |
| 72959 | female | 68.04 |
| 511 | other | 0.48 |
| 27463 | null | 25.61 |


### Review Author Genders for FanFiktion.de
```javascript
let uniqueReviewersFF = db.reviews.distinct('userId', { source: 'FanFiktion' }).length

db.reviews.aggregate([
	{
		$match: { source: 'FanFiktion' }
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
			quantity: { $sum: 1 }
		}
	},
    {
        $project: {
            _id: 0,
            gender: '$_id',
            frequency: '$quantity',
            percent: { $round: [{ $multiply: [{ $divide: [ '$quantity', uniqueReviewersFF ]}, 100 ]}, 2]},
        }
    }
])
```
| frequency | gender | percent |
| :--- | :--- | :--- |
| 51084 | female | 67.89 |
| 19185 | null | 25.5 |
| 4521 | male | 6.01 |
| 450 | other | 0.6 |


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
			sumFemaleChars: { $sum: '$genders.females' },
			sumMaleChars: { $sum: '$genders.males' },
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
			authorGender: '$_id',
			femaleCharsPercent: { $round: [{ $multiply: [{ $divide: [ '$sumFemaleChars', { $sum: ['$sumFemaleChars', '$sumMaleChars'] } ]}, 100 ]}, 2]},
			maleCharsPercent: { $round: [{ $multiply: [{ $divide: [ '$sumMaleChars', { $sum: ['$sumFemaleChars', '$sumMaleChars'] } ]}, 100 ]}, 2]},
			femalePronounsPercent: { $round: [{ $multiply: [{ $divide: [ { $sum: ['$prnIhr', '$prnIhrer', '$prnSie'] }, { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]},
			malePronounsPercent: { $round: [{ $multiply: [{ $divide: [ { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnSeiner'] }, { $sum: ['$prnEr', '$prnIhm', '$prnIhn', '$prnIhr', '$prnIhrer', '$prnSeiner', '$prnSie'] } ]}, 100 ]}, 2]}
		}
	}
])
```
| authorGender | femaleCharsPercent | femalePronounsPercent | maleCharsPercent | malePronounsPercent |
| :--- | :--- | :--- | :--- | :--- |
| other | 31.03 | 31.69 | 68.97 | 68.31 |
| null | 31.85 | 31.82 | 68.15 | 68.18 |
| male | 34.52 | 35.64 | 65.48 | 64.36 |
| female | 35.82 | 37.66 | 64.18 | 62.34 |


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
| authorAge | count | femaleCharsPercent | femalePronounsPercent | maleCharsPercent | malePronounsPercent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1-20 | 15380 | 39.18 | 41.9 | 60.82 | 58.1 |
| 21-25 | 70171 | 38.51 | 38.93 | 61.49 | 61.07 |
| 26-30 | 64502 | 37.14 | 38.69 | 62.86 | 61.31 |
| 31+ | 56684 | 33.42 | 35.18 | 66.58 | 64.82 |


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
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1-20 | 0.61 | 0.62 | 5.2 | 73.52 | 19.07 | 1.41 | 0.18 | 0.58 |
| 31+ | 0.67 | 0.57 | 3.25 | 64.25 | 31.52 | 0.35 | 0.07 | 0.65 |
| 26-30 | 0.63 | 0.57 | 2.56 | 67.96 | 28.43 | 0.44 | 0.04 | 0.61 |
| 21-25 | 0.61 | 0.28 | 2.95 | 71.95 | 24.12 | 0.62 | 0.08 | 0.61 |


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
| count | femaleAuthorPercent | femaleAuthors | genre | maleAuthorPercent | maleAuthors | nullAuthorPercent | nullAuthors | otherAuthorPercent | otherAuthors |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 107045 | 76.2 | 81571 | Anime & Manga | 6.09 | 6516 | 16.9 | 18089 | 0.81 | 869 |
| 106007 | 75.3 | 79826 | Bücher | 4.54 | 4810 | 19.39 | 20559 | 0.77 | 812 |
| 75854 | 76.34 | 57907 | Prominente | 2.65 | 2012 | 20.17 | 15296 | 0.84 | 639 |
| 51942 | 75.67 | 39302 | Serien & Podcasts | 3.07 | 1596 | 20.41 | 10602 | 0.85 | 442 |
| 19093 | 70.03 | 13371 | Kino- & TV-Filme | 8 | 1527 | 20.67 | 3947 | 1.3 | 248 |
| 16923 | 65.24 | 11041 | Computerspiele | 14.31 | 2421 | 19.36 | 3276 | 1.09 | 185 |
| 9064 | 65.72 | 5957 | Cartoons & Comics | 12.41 | 1125 | 20.53 | 1861 | 1.33 | 121 |
| 5414 | 63.96 | 3463 | Crossover | 13.32 | 721 | 21.72 | 1176 | 1 | 54 |
| 2738 | 76.52 | 2095 | Musicals | 3.1 | 85 | 17.35 | 475 | 3.03 | 83 |
| 768 | 30.21 | 232 | Tabletop- & Rollenspiele | 40.76 | 313 | 28.78 | 221 | 0.26 | 2 |

