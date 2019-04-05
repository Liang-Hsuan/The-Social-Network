DROP DATABASE IF EXISTS `TheSocialNetwork_G7`;
CREATE DATABASE `TheSocialNetwork_G7`;
USE `TheSocialNetwork_G7`;

DROP TABLE IF EXISTS `User`;

CREATE TABLE `User` (
  `userName` varchar(20) NOT NULL,
  `firstName` varchar(100) DEFAULT NULL,
  `lastName` varchar(100) DEFAULT NULL,
  `birthDay` date DEFAULT NULL,
  `gender` char(1) DEFAULT NULL,
  PRIMARY KEY (`userName`)
);

INSERT INTO `User` (`userName`, `firstName`, `lastName`, `birthDay`, `gender`)
VALUES
	('fuduji','Fudu','Jun','2000-01-01','m'),
	('sosososophia','Sophia','Liu','2000-04-01','f');

DROP TABLE IF EXISTS `Follow`;

CREATE TABLE `Follow` (
  `followee` varchar(20) NOT NULL,
  `follower` varchar(20) NOT NULL,
  PRIMARY KEY (`followee`,`follower`),
  KEY `follower` (`follower`),
  CONSTRAINT `follow_ibfk_1` FOREIGN KEY (`followee`) REFERENCES `User` (`userName`),
  CONSTRAINT `follow_ibfk_2` FOREIGN KEY (`follower`) REFERENCES `User` (`userName`)
);

INSERT INTO `Follow` (`followee`, `follower`)
VALUES
	('fuduji','sosososophia');

DROP TABLE IF EXISTS `Grouping`;

CREATE TABLE `Grouping` (
  `groupID` int(11) NOT NULL AUTO_INCREMENT,
  `groupName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`groupID`)
);

INSERT INTO `Grouping` (`groupID`, `groupName`)
VALUES
	(1,'Gamers Paradise'),
	(2,'Sports Heaven');

DROP TABLE IF EXISTS `GroupMember`;

CREATE TABLE `GroupMember` (
  `userName` varchar(20) NOT NULL,
  `groupID` int(11) NOT NULL,
  PRIMARY KEY (`userName`,`groupID`),
  KEY `groupID` (`groupID`),
  CONSTRAINT `groupmember_ibfk_1` FOREIGN KEY (`userName`) REFERENCES `User` (`userName`),
  CONSTRAINT `groupmember_ibfk_2` FOREIGN KEY (`groupID`) REFERENCES `Grouping` (`groupID`)
);

INSERT INTO `GroupMember` (`userName`, `groupID`)
VALUES
	('fuduji',1),
	('sosososophia',1);

DROP TABLE IF EXISTS `Topic`;

CREATE TABLE `Topic` (
  `topicName` varchar(100) NOT NULL,
  PRIMARY KEY (`topicName`)
);

INSERT INTO `Topic` (`topicName`)
VALUES
	('Baseball'),
	('Foosball'),
	('Games'),
	('Pokemon'),
	('PUBG'),
	('Sports');

DROP TABLE IF EXISTS `ParentTopic`;

CREATE TABLE `ParentTopic` (
  `topicName` varchar(100) NOT NULL,
  `parentTopicName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`topicName`),
  KEY `parentTopicName` (`parentTopicName`),
  CONSTRAINT `parenttopic_ibfk_1` FOREIGN KEY (`topicName`) REFERENCES `Topic` (`topicName`),
  CONSTRAINT `parenttopic_ibfk_2` FOREIGN KEY (`parentTopicName`) REFERENCES `Topic` (`topicName`)
);

INSERT INTO `ParentTopic` (`topicName`, `parentTopicName`)
VALUES
	('Pokemon','Games'),
	('PUBG','Games'),
	('Baseball','Sports'),
	('Foosball','Sports');

DROP TABLE IF EXISTS `Post`;

CREATE TABLE `Post` (
  `postID` int(11) NOT NULL AUTO_INCREMENT,
  `postText` text,
  `postLinks` varchar(200) DEFAULT NULL,
  `postImages` varchar(200) DEFAULT NULL,
  `likes` int(11) DEFAULT '0',
  `dislikes` int(11) DEFAULT '0',
  `parentPostID` int(11) DEFAULT NULL,
  `createTime` datetime NOT NULL,
  PRIMARY KEY (`postID`)
);

INSERT INTO `Post` (`postID`, `postText`, `postLinks`, `postImages`, `likes`, `dislikes`, `parentPostID`, `createTime`)
VALUES
	(1,'PUBG is the best game ever!!!!!!!',NULL,NULL,1,1,NULL,'2019-04-04 16:01:01'),
	(2,' Who agree with me???',NULL,NULL,0,0,1,'2019-04-04 16:04:01'),
	(3,' Like and Share ASAP!!!',NULL,NULL,0,0,2,'2019-04-04 16:10:01'),
	(4,' Pokemon is the best!!!!! OK?????',NULL,NULL,0,1,2,'2019-04-04 16:15:01'),
	(5,' Bullshit!!!',NULL,NULL,0,0,4,'2019-04-04 16:16:01'),
	(6,'Pokemon sucks!!! Worst game ever!!!',NULL,NULL,0,1,NULL,'2019-04-04 16:20:01'),
	(7,' Bullshit!!!!',NULL,NULL,0,1,6,'2019-04-04 16:21:01'),
	(8,'Report by NY Times: Sleeping - Best sports ever!',NULL,NULL,2,0,NULL,'2019-04-04 16:25:01'),
	(9,' Peace and Love~~~',NULL,NULL,0,0,8,'2019-04-04 16:30:01');

DROP TABLE IF EXISTS `Posting`;

CREATE TABLE `Posting` (
  `userName` varchar(20) NOT NULL,
  `postID` int(11) NOT NULL,
  PRIMARY KEY (`userName`,`postID`),
  KEY `postID` (`postID`),
  CONSTRAINT `posting_ibfk_1` FOREIGN KEY (`userName`) REFERENCES `User` (`userName`),
  CONSTRAINT `posting_ibfk_2` FOREIGN KEY (`postID`) REFERENCES `Post` (`postID`)
);

INSERT INTO `Posting` (`userName`, `postID`)
VALUES
	('fuduji',1),
	('fuduji',2),
	('fuduji',3),
	('sosososophia',4),
	('fuduji',5),
	('fuduji',6),
	('sosososophia',7),
	('fuduji',8),
	('sosososophia',9);

DROP TABLE IF EXISTS `PostTagTopic`;

CREATE TABLE `PostTagTopic` (
  `postID` int(11) NOT NULL,
  `topicName` varchar(100) NOT NULL,
  PRIMARY KEY (`postID`,`topicName`),
  KEY `topicName` (`topicName`),
  CONSTRAINT `posttagtopic_ibfk_1` FOREIGN KEY (`postID`) REFERENCES `Post` (`postID`),
  CONSTRAINT `posttagtopic_ibfk_2` FOREIGN KEY (`topicName`) REFERENCES `Topic` (`topicName`)
);

INSERT INTO `PostTagTopic` (`postID`, `topicName`)
VALUES
	(1,'Games'),
	(6,'Pokemon'),
	(1,'PUBG'),
	(8,'Sports');

DROP TABLE IF EXISTS `UserFollowTopic`;

CREATE TABLE `UserFollowTopic` (
  `userName` varchar(20) NOT NULL,
  `topicName` varchar(100) NOT NULL,
  PRIMARY KEY (`userName`,`topicName`),
  KEY `topicName` (`topicName`),
  CONSTRAINT `userfollowtopic_ibfk_1` FOREIGN KEY (`userName`) REFERENCES `User` (`userName`),
  CONSTRAINT `userfollowtopic_ibfk_2` FOREIGN KEY (`topicName`) REFERENCES `Topic` (`topicName`)
);

INSERT INTO `UserFollowTopic` (`userName`, `topicName`)
VALUES
	('fuduji','Games'),
	('sosososophia','Games');

DROP TABLE IF EXISTS `UserRead`;

CREATE TABLE `UserRead` (
  `userName` varchar(20) NOT NULL,
  `postID` int(11) NOT NULL,
  `readTime` datetime NOT NULL,
  PRIMARY KEY (`userName`,`postID`),
  KEY `postID` (`postID`),
  CONSTRAINT `userread_ibfk_1` FOREIGN KEY (`userName`) REFERENCES `User` (`userName`),
  CONSTRAINT `userread_ibfk_2` FOREIGN KEY (`postID`) REFERENCES `Post` (`postID`)
);

INSERT INTO `UserRead` (`userName`, `postID`, `readTime`)
VALUES
	('fuduji',1,'2019-04-04 16:02:01'),
	('sosososophia',1,'2019-04-04 16:04:01'),
	('fuduji',6,'2019-04-04 16:21:01'),
	('sosososophia',6,'2019-04-04 16:20:30'),
	('sosososophia',8,'2019-04-04 16:26:01');
