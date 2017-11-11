--
-- Inmate Learners
--
DROP TABLE IF EXISTS `inmate`;
CREATE TABLE `inmate` (
    `id`     int(10) unsigned NOT NULL AUTO_INCREMENT,
    `fname`  varchar(63)      NOT NULL,
    `minit`  char(1)          DEFAULT NULL,
    `lname`  varchar(63)      NOT NULL,
    `dob`    date             NOT NULL,
    `wallet` int(10) unsigned DEFAULT 0,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


