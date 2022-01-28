CREATE TABLE `sources`
(
    `_id`  BIGINT PRIMARY KEY,
    `name` VARCHAR(255),
    `url`  VARCHAR(255)
);

CREATE TABLE `series`
(
    `_id`   BIGINT PRIMARY KEY,
    `title` VARCHAR(255)
);

CREATE TABLE `series_stories`
(
    `seriesId` BIGINT,
    `storyId`  BIGINT
);

CREATE TABLE `stories`
(
    `_id`         BIGINT PRIMARY KEY,
    `title`       VARCHAR(255),
    `url`         VARCHAR(255),
    `summary`     TEXT,
    `status`      ENUM ('work in progress', 'done', 'paused', 'cancelled'),
    `likes`       BIGINT,
    `follows`     BIGINT,
    `hits`        BIGINT,
    `sourceId`    BIGINT,
    `authorId`    BIGINT,
    `genreId`     BIGINT,
    `ratingId`    BIGINT,
    `categoryId`  BIGINT,
    `pairingId`   BIGINT,
    `publishedOn` DATE,
    `reviewedOn`  DATE
);

CREATE TABLE `chapters`
(
    `_id`         BIGINT PRIMARY KEY,
    `number`      BIGINT,
    `title`       VARCHAR(255),
    `content`     LONGTEXT,
    `notes`       TEXT,
    `publishedOn` DATE,
    `reviewedOn`  DATE,
    `storyId`     BIGINT
);

CREATE TABLE `story_topics`
(
    `storyId` BIGINT,
    `topicId` BIGINT
);

CREATE TABLE `story_fandoms`
(
    `storyId`  BIGINT,
    `fandomId` BIGINT
);

CREATE TABLE `users`
(
    `_id`       BIGINT PRIMARY KEY,
    `url`       VARCHAR(255),
    `username`  VARCHAR(255),
    `firstName` VARCHAR(255),
    `lastName`  VARCHAR(255),
    `joinedOn`  DATE,
    `locatedAt` VARCHAR(255),
    `country`   VARCHAR(255),
    `gender`    ENUM ('male', 'female', 'other'),
    `age`       VARCHAR(255),
    `bio`       LONGTEXT,
    `sourceId`  BIGINT
);

CREATE TABLE `favored_stories`
(
    `userId`  BIGINT,
    `storyId` BIGINT
);

CREATE TABLE `favored_authors`
(
    `userId`   BIGINT,
    `authorId` BIGINT
);

CREATE TABLE `genres`
(
    `_id`   BIGINT PRIMARY KEY,
    `name1` VARCHAR(255),
    `name2` VARCHAR(255),
    `name3` VARCHAR(255)
);

CREATE TABLE `topics`
(
    `_id`   BIGINT PRIMARY KEY,
    `name1` VARCHAR(255),
    `name2` VARCHAR(255),
    `name3` VARCHAR(255)
);

CREATE TABLE `categories`
(
    `_id`   BIGINT PRIMARY KEY,
    `name1` VARCHAR(255),
    `name2` VARCHAR(255),
    `name3` VARCHAR(255)
);

CREATE TABLE `fandoms`
(
    `_id`     BIGINT PRIMARY KEY,
    `genreId` BIGINT,
    `name1`   VARCHAR(255),
    `name2`   VARCHAR(255),
    `name3`   VARCHAR(255)
);

CREATE TABLE `characters`
(
    `_id`      BIGINT PRIMARY KEY,
    `name1`    VARCHAR(255),
    `name2`    VARCHAR(255),
    `name3`    VARCHAR(255),
    `fandomId` BIGINT
);

CREATE TABLE `story_characters`
(
    `storyId`     BIGINT,
    `characterId` BIGINT
);

CREATE TABLE `ratings`
(
    `_id`   BIGINT PRIMARY KEY,
    `name1` VARCHAR(255),
    `name2` VARCHAR(255),
    `name3` VARCHAR(255)
);

CREATE TABLE `tags`
(
    `_id`  BIGINT PRIMARY KEY,
    `name` VARCHAR(255)
);

CREATE TABLE `story_tags`
(
    `storyId` BIGINT,
    `tagId`   BIGINT
);

CREATE TABLE `pairings`
(
    `_id`   BIGINT PRIMARY KEY,
    `name1` VARCHAR(255),
    `name2` VARCHAR(255),
    `name3` VARCHAR(255)
);

CREATE TABLE `reviews`
(
    `_id`            BIGINT PRIMARY KEY,
    `userId`         BIGINT,
    `content`        TEXT,
    `reviewedOn`     DATETIME,
    `parentId`       BIGINT,
    `reviewableType` VARCHAR(255) COMMENT 'Story or Chapter',
    `reviewableId`   BIGINT
);

ALTER TABLE `series_stories`
    ADD FOREIGN KEY (`seriesId`) REFERENCES `series` (`_id`);

ALTER TABLE `series_stories`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `stories`
    ADD FOREIGN KEY (`sourceId`) REFERENCES `sources` (`_id`);

ALTER TABLE `stories`
    ADD FOREIGN KEY (`authorId`) REFERENCES `users` (`_id`);

ALTER TABLE `stories`
    ADD FOREIGN KEY (`genreId`) REFERENCES `genres` (`_id`);

ALTER TABLE `stories`
    ADD FOREIGN KEY (`ratingId`) REFERENCES `ratings` (`_id`);

ALTER TABLE `chapters`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `story_topics`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `story_topics`
    ADD FOREIGN KEY (`topicId`) REFERENCES `topics` (`_id`);

ALTER TABLE `story_fandoms`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `story_fandoms`
    ADD FOREIGN KEY (`fandomId`) REFERENCES `fandoms` (`_id`);

ALTER TABLE `favored_stories`
    ADD FOREIGN KEY (`userId`) REFERENCES `users` (`_id`);

ALTER TABLE `favored_stories`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `favored_authors`
    ADD FOREIGN KEY (`userId`) REFERENCES `users` (`_id`);

ALTER TABLE `favored_authors`
    ADD FOREIGN KEY (`authorId`) REFERENCES `users` (`_id`);

ALTER TABLE `characters`
    ADD FOREIGN KEY (`fandomId`) REFERENCES `fandoms` (`_id`);

ALTER TABLE `story_characters`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `story_characters`
    ADD FOREIGN KEY (`characterId`) REFERENCES `characters` (`_id`);

ALTER TABLE `story_tags`
    ADD FOREIGN KEY (`storyId`) REFERENCES `stories` (`_id`);

ALTER TABLE `story_tags`
    ADD FOREIGN KEY (`tagId`) REFERENCES `tags` (`_id`);

ALTER TABLE `reviews`
    ADD FOREIGN KEY (`userId`) REFERENCES `users` (`_id`);

ALTER TABLE `reviews`
    ADD FOREIGN KEY (`parentId`) REFERENCES `reviews` (`_id`);
