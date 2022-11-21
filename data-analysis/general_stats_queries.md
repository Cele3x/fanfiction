# General Statistics Queries

### Scraping Time Period

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			minCreatedAt: {$min: "$createdAt"},
			maxCreatedAt: {$max: "$createdAt"},
			minUpdatedAt: {$min: "$updatedAt"},
			maxUpdatedAt: {$max: "$updatedAt"}
		}
	},
])
```

| archive         | maxCreatedAt             | maxUpdatedAt             | minCreatedAt             | minUpdatedAt             |
|:----------------|:-------------------------|:-------------------------|:-------------------------|:-------------------------|
| FanFiktion      | 2022-08-23T08:58:55.600Z | 2022-08-23T11:51:34.930Z | 2022-01-28T15:03:34.827Z | 2022-01-31T09:21:16.908Z |
| ArchiveOfOurOwn | 2022-08-08T10:13:03.154Z | 2022-08-08T10:13:03.154Z | 2022-07-25T16:29:34.428Z | 2022-07-25T16:29:34.428Z |

### Stories per Source

```javascript
db.stories.aggregate([
	{
		$group: {
			_id: '$source',
			storyCount: {$sum: 1}
		}
	}
])
```

| archive         | storyCount |
|:----------------|:-----------|
| FanFiktion      | 394,848    |
| ArchiveOfOurOwn | 18,075     |

### Chapters per Source

```javascript
db.chapters.aggregate([
	{
		$group: {
			_id: '$source',
			storyCount: {$sum: 1}
		}
	}
])
```

| archive         | storyCount |
|:----------------|:-----------|
| ArchiveOfOurOwn | 70,857     |
| FanFiktion      | 1,885,066  |

### Users per Source

```javascript
db.users.aggregate([
	{
		$group: {
			_id: '$source',
			userCount: {$sum: 1}
		}
	}
])
```

| archive         | userCount |
|:----------------|:----------|
| FanFiktion      | 135,726   |
| ArchiveOfOurOwn | 14,249    |

### Reviews per Source

```javascript
db.reviews.aggregate([
	{
		$group: {
			_id: '$source',
			reviewCount: {$sum: 1}
		}
	}
])
```

| archive         | reviewCount |
|:----------------|:------------|
| FanFiktion      | 4,849,646   |
| ArchiveOfOurOwn | 37,721      |

