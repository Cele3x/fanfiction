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
