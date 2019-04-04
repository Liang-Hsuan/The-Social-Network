DROP DATABASE IF EXISTS TheSocialNetwork_G7;
CREATE DATABASE TheSocialNetwork_G7;
USE TheSocialNetwork_G7;

CREATE TABLE User(
  userName VARCHAR(20) NOT NULL,
  firstName VARCHAR(100) DEFAULT NULL,
  lastName VARCHAR(100) DEFAULT NULL,
  birthDay DATE DEFAULT NULL,
  gender CHAR(1) DEFAULT NULL,
  primary key (userName)
);

CREATE TABLE Follow(
  followee VARCHAR(20) NOT NULL,
  follower VARCHAR(20) NOT NULL,
  primary key (followee, follower),
  foreign key (followee) references User(userName),
  foreign key (follower) references User(userName)
);

CREATE TABLE Grouping(
  groupID INT NOT NULL AUTO_INCREMENT,
  groupName VARCHAR(100) DEFAULT NULL,
  primary key (groupID)
);

CREATE TABLE GroupMember(
  userName VARCHAR(20) NOT NULL,
  groupID INT NOT NULL,
  primary key (userName, groupID),
  foreign key (userName) references User(userName),
  foreign key (groupID) references Grouping(groupID)
);

CREATE TABLE Topic(
  topicName VARCHAR(100) NOT NULL,
  primary key (topicName)
);

CREATE TABLE ParentTopic(
  topicName VARCHAR(100) NOT NULL,
  parentTopicName VARCHAR(100),
  primary key (topicName),
  foreign key (topicName) references Topic(topicName),
  foreign key (parentTopicName) references Topic(topicName)
);

CREATE TABLE Post(
  postID INT NOT NULL AUTO_INCREMENT,
  postText TEXT,
  postLinks VARCHAR(200) DEFAULT NULL,
  postImages VARCHAR(200) DEFAULT NULL,
  likes INT DEFAULT '0',
  dislikes INT DEFAULT '0',
  parentPostID INT DEFAULT NULL,
  createTime DATE NOT NULL,
  primary key (postID)
);

CREATE TABLE PostTagTopic(
  postID INT NOT NULL,
  topicName VARCHAR(100) NOT NULL,
  primary key (postID, topicName),
  foreign key (postID) references Post(postID),
  foreign key (topicName) references Topic(topicName)
);

CREATE TABLE Posting(
  userName VARCHAR(20) NOT NULL,
  postID INT NOT NULL,
  primary key (userName, postID),
  foreign key (userName) references User(userName),
  foreign key (postID) references Post(postID)
);

CREATE TABLE UserFollowTopic(
  userName VARCHAR(20) NOT NULL,
  topicName VARCHAR(100) NOT NULL,
  primary key (userName, topicName),
  foreign key (userName) references User(userName),
  foreign key (topicName) references Topic(topicName)
);

CREATE TABLE UserRead(
  userName VARCHAR(20) NOT NULL,
  postID INT NOT NULL,
  primary key (userName, postID),
  foreign key (userName) references User(userName),
  foreign key (postID) references Post(postID)
);
