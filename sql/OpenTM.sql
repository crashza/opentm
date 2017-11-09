DROP TABLE IF EXISTS `destinations`;
CREATE TABLE `destinations` (
  `i_destination` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `prefix` varchar(30) NOT NULL,
  `i_group` mediumint(8) unsigned NOT NULL,
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`i_destination`),
  UNIQUE KEY `prefix` (`prefix`)
) ENGINE=InnoDB AUTO_INCREMENT=80741 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `groups`;
CREATE TABLE `groups` (
  `i_group` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`i_group`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `product_defs`;
CREATE TABLE `product_defs` (
  `i_product` mediumint(8) unsigned NOT NULL,
  `i_group` mediumint(8) unsigned NOT NULL,
  `value` varchar(64) NOT NULL DEFAULT '0.0000000000',
  `charge_type` int(2) NOT NULL,
  `i_vendor` mediumint(8) unsigned NOT NULL,
  PRIMARY KEY (`i_product`,`i_group`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `products`;
CREATE TABLE `products` (
  `i_product` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(128) NOT NULL,
  PRIMARY KEY (`i_product`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `vendor_rates`;
CREATE TABLE `vendor_rates` (
  `i_destination` mediumint(8) unsigned NOT NULL,
  `i_vendor` mediumint(8) unsigned NOT NULL,
  `price` decimal(14,10) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'O',
  `last_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`i_destination`,`i_vendor`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `vendors`;
CREATE TABLE `vendors` (
  `i_vendor` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(128) NOT NULL,
  PRIMARY KEY (`i_vendor`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `charge_types`;
CREATE TABLE `charge_types` (
  `i_charge_type` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`i_charge_type`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

INSERT INTO `charge_types` VALUES (3,'COST_PLUS_PERC'),(2,'COST_PLUS_VALUE'),(1,'FLAT'),(4,'FORMULA');

