CREATE TABLE User(
  userName VARCHAR(20) NOT NULL,
  firstName VARCHAR(100) DEFAULT NULL,
  lastName VARCHAR(100) DEFAULT NULL,
  birthDate INT(11) DEFAULT NULL,
  birthMonth INT(11) DEFAULT NULL,
  birthYear INT(11) DEFAULT NULL,
  gender CHAR(1) DEFAULT NULL,
  primary key (userName)
);

CREATE TABLE Follow(
  followee VARCHAR(20) NOT NULL,
  follower VARCHAR(20) NOT NULL,
  primary key (followee, follower)
  foreign key (followee) references User(userName),
  foreign key (follower) references User(userName)
);

CREATE TABLE Group(
  groupID INT NOT NULL,
  groupName VARCHAR(100) DEFAULT NULL,
  primary key (groupID)
);

CREATE TABLE GroupMember(
  userName VARCHAR(20) NOT NULL,
  groupID INT DEFAULT NULL,
  primary key (userName, groupID),
  foreign key (userName) references User(userName),
  foreign key (groupID) references Group(groupID)
);

CREATE TABLE Topic(
  topicName VARCHAR(100) NOT NULL,
  parentTopicName VARCHAR(100) DEFAULT NULL,
  primary key (topicName)
);

CREATE TABLE Post(
  postID INT NOT NULL,
  authorUserName VARCHAR(20) NOT NULL,
  postText TEXT,
  postLinks VARCHAR(200) DEFAULT NULL,
  postImages VARCHAR(200) DEFAULT NULL,
  likes INT DEFAULT '0',
  disliks INT DEFAULT '0',
  parentPostID INT DEFAULT NULL,
  createTime DATE NOT NULL,
  primary key (postID),
  foreign key (authorUserName) references User(userName)
);

CREATE TABLE PostTagTopic(
  postID INT NOT NULL,
  topicName VARCHAR(100) DEFAULT NULL,
  primary key (postID, topicName),
  foreign key (postID) references Post(postID),
  foreign key (topicName) references Topic(topicName)
);

CREATE TABLE UserFollowTopic(
  userName VARCHAR(20) NOT NULL,
  topicName VARCHAR(100) DEFAULT NULL,
  primary key (userName, topicName),
  foreign key (userName) references User(userName),
  foreign key (topicName) references Topic(topicName)
);

CREATE TABLE Read(
  userName VARCHAR(20) NOT NULL,
  postID INT DEFAULT NULL,
  primary key (userName, postID),
  foreign key (userName) references User(userName),
  foreign key (postID) references Post(postID)
);
