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
