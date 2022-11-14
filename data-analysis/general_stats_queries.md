# General Statistics Queries

### Scraping Time Period
```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			minCreatedAt: { $min: "$createdAt" },
			maxCreatedAt: { $max: "$createdAt" },
			minUpdatedAt: { $min: "$updatedAt" },
			maxUpdatedAt: { $max: "$updatedAt" }
		}
	},
])
```

### Stories per Source
```javascript
db.stories.aggregate([
    {
        $group: {
            _id: '$source',
            storyCount: { $sum: 1 }
        }
    }
])
```

### Chapters per Source
```javascript
db.chapters.aggregate([
    {
        $group: {
            _id: '$source',
            storyCount: { $sum: 1 }
        }
    }
])
```

### Users per Source
```javascript
db.users.aggregate([
    {
        $group: {
            _id: '$source',
            userCount: { $sum: 1 }
        }
    }
])
```

### Reviews per Source
```javascript
db.reviews.aggregate([
    {
        $group: {
            _id: '$source',
            reviewCount: { $sum: 1 }
        }
    }
])
```
