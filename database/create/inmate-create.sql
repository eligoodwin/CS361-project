--
-- Inmate Learners
--
DROP TABLE IF EXISTS `inmate`;
CREATE TABLE `inmate` (
    `id`       int(10) unsigned NOT NULL AUTO_INCREMENT,
    `fname`    varchar(63)      NOT NULL,
    `minit`    char(1)          DEFAULT NULL,
    `lname`    varchar(63)      NOT NULL,
    `dob`      date             NOT NULL,
    `wallet`   int(10) unsigned DEFAULT 0,
    `username` varchar(63)      DEFAULT NULL,
    `password` varchar(63)      DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `inmate_learning_resources`;
CREATE TABLE `inmate_learning_resources`(
	`prisonerID` int(10) NOT NULL,
	`moduleID` int(10) NOT NULL,
	PRIMARY KEY (`prisonerID`),
	FOREIGN KEY (`prisonerID`) REFERENCES inmate(id),
	FOREIGN KEY (`moduleID`) REFERENCES learning_module(moduleID)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `learning_module`;
CREATE TABLE `learning_module`(
	`moduleID` int(10) NOT NULL AUTO_INCREMENT,
	`module_name` varchar(256) NOT NULL,
	`module_data` text NOT NULL,
	`module_summary` varchar(256) NOT NULL,
	PRIMARY KEY	(`moduleID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `question`;
CREATE TABLE `question`(
	`questionID` int(10) NOT NULL AUTO_INCREMENT,
	`moduleID` int(10) NOT NULL,
	`question` varchar(256) NOT NULL,
	`correctAnswerID` int(10) NOT NULL,
	FOREIGN KEY (`correctAnswerID`) REFERENCES answer(answerID),
	FOREIGN KEY (`moduleID`) REFERENCES learning_module(moduleID),
	PRIMARY KEY (`questionID`)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `answer`;
CREATE TABLE `answer`(
	`answerID` int(10) NOT NULL AUTO_INCREMENT,
	`moduleID` int(10) NOT NULL,
	`answer` varchar(256) NOT NULL,
	PRIMARY KEY (`answerID`)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;
