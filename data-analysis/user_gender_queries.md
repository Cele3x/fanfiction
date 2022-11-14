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
// 
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
