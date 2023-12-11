-- MySQL dump 10.13  Distrib 8.0.30, for macos12 (x86_64)
--
-- Host: localhost    Database: loan
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Bank`
--

DROP TABLE IF EXISTS `Bank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bank` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `name` varchar(255) DEFAULT NULL,
  `rate` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bank`
--

LOCK TABLES `Bank` WRITE;
/*!40000 ALTER TABLE `Bank` DISABLE KEYS */;
INSERT INTO `Bank` VALUES (1,'中国银行',0.049),(2,'工商银行',0.05),(3,'建设银行',0.048);
/*!40000 ALTER TABLE `Bank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BankLoan`
--

DROP TABLE IF EXISTS `BankLoan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BankLoan` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `bankId` int DEFAULT NULL,
  `userId` int DEFAULT NULL,
  `loan_type` int DEFAULT NULL,
  `repay_type` int DEFAULT NULL,
  `term` int DEFAULT NULL,
  `d_rate` float DEFAULT NULL,
  `b_amount` float DEFAULT NULL,
  `b_interest` float DEFAULT NULL,
  `b_total_pay` float DEFAULT NULL,
  `b_monthly_pay` float DEFAULT NULL,
  `b_monthly_decrement` float DEFAULT NULL,
  `loan_time` text,
  `auto_judge` int DEFAULT NULL,
  `manual_judge` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bankId` (`bankId`),
  KEY `userId` (`userId`),
  CONSTRAINT `bankloan_ibfk_1` FOREIGN KEY (`bankId`) REFERENCES `Bank` (`id`),
  CONSTRAINT `bankloan_ibfk_2` FOREIGN KEY (`userId`) REFERENCES `User` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BankLoan`
--

LOCK TABLES `BankLoan` WRITE;
/*!40000 ALTER TABLE `BankLoan` DISABLE KEYS */;
INSERT INTO `BankLoan` VALUES (8,1,1,2,2,25,0.035,3000000,1316880,4316880,18750,29.17,'20221220012913',0,1),(9,1,1,2,1,30,0.035,200000,123312,323312,898.09,0,'20221220013946',0,1),(10,1,1,2,1,30,0.035,30000,18496.8,48496.8,134.71,0,'20221220014824',1,1),(12,1,1,2,1,5,0.035,423323,38736,462059,7700.98,0,'20221220161800',1,1),(13,1,1,2,2,30,0.035,533242,280730,813972,3036.52,4.32,'20221220163910',0,1),(21,2,1,2,1,30,0.0475,800000,702344,1502340,4173.18,0,'20221224154400',1,1),(24,1,1,2,1,5,0.049,32523,4212.61,36735.6,612.26,0,'20221224180512',1,1),(25,1,1,2,1,5,0.049,34223,4432.81,38655.8,644.26,0,'20221224193342',1,0);
/*!40000 ALTER TABLE `BankLoan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BankUser`
--

DROP TABLE IF EXISTS `BankUser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BankUser` (
  `bankId` int NOT NULL,
  `userId` int NOT NULL,
  `deposit` int DEFAULT NULL,
  `quota` int DEFAULT NULL,
  `discount` float DEFAULT NULL,
  PRIMARY KEY (`bankId`,`userId`),
  KEY `userId` (`userId`),
  CONSTRAINT `bankuser_ibfk_1` FOREIGN KEY (`bankId`) REFERENCES `Bank` (`id`),
  CONSTRAINT `bankuser_ibfk_2` FOREIGN KEY (`userId`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BankUser`
--

LOCK TABLES `BankUser` WRITE;
/*!40000 ALTER TABLE `BankUser` DISABLE KEYS */;
INSERT INTO `BankUser` VALUES (1,1,100000,200000,1),(1,2,0,100000,1.1),(1,3,2000000,3000000,0.95),(1,4,300000,1000000,0.95),(1,5,50000,300000,1),(2,1,500000,1000000,0.95),(2,2,1000000,1500000,0.95),(2,3,0,200000,1),(2,4,1000000,5000000,0.98),(2,5,0,200000,1),(3,1,0,200000,1),(3,2,50000,300000,1),(3,3,0,200000,1),(3,4,200000,300000,1),(3,5,2000000,5000000,0.95);
/*!40000 ALTER TABLE `BankUser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FundLoan`
--

DROP TABLE IF EXISTS `FundLoan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FundLoan` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `userId` int DEFAULT NULL,
  `loan_type` int DEFAULT NULL,
  `repay_type` int DEFAULT NULL,
  `term` int DEFAULT NULL,
  `f_rate` float DEFAULT NULL,
  `f_amount` float DEFAULT NULL,
  `f_interest` float DEFAULT NULL,
  `f_total_pay` float DEFAULT NULL,
  `f_monthly_pay` float DEFAULT NULL,
  `f_monthly_decrement` float DEFAULT NULL,
  `loan_time` text,
  `auto_judge` int DEFAULT NULL,
  `manual_judge` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `userId` (`userId`),
  CONSTRAINT `fundloan_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `User` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FundLoan`
--

LOCK TABLES `FundLoan` WRITE;
/*!40000 ALTER TABLE `FundLoan` DISABLE KEYS */;
INSERT INTO `FundLoan` VALUES (4,1,2,2,25,0.0325,100000,40760.4,140760,604.17,0.9,'20221220012913',1,1),(5,1,2,1,30,0.0325,1000000,566743,1566740,4352.06,0,'20221220013946',0,1),(6,1,2,1,30,0.0325,1000000,566743,1566740,4352.06,0,'20221220014824',0,1),(8,1,2,1,5,0.0325,432523,36678,469201,7820.02,0,'20221220161800',0,1),(9,1,2,2,30,0.0325,325253,159001,484254,1784.37,2.45,'20221220163910',1,1),(10,1,2,1,30,0.0325,200000,113349,313349,870.41,0,'20221224154400',0,1),(11,1,2,1,5,0.0325,4234,359.04,4593.04,76.55,0,'20221224180512',1,1),(12,1,2,1,5,0.0325,423432,35907.1,459339,7655.65,0,'20221224193342',0,1);
/*!40000 ALTER TABLE `FundLoan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FundUser`
--

DROP TABLE IF EXISTS `FundUser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FundUser` (
  `userId` int NOT NULL,
  `deposit` int DEFAULT NULL,
  `quota` int DEFAULT NULL,
  `rate` float DEFAULT NULL,
  `f_month` int DEFAULT NULL,
  PRIMARY KEY (`userId`),
  CONSTRAINT `funduser_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FundUser`
--

LOCK TABLES `FundUser` WRITE;
/*!40000 ALTER TABLE `FundUser` DISABLE KEYS */;
INSERT INTO `FundUser` VALUES (1,100000,200000,0.0325,20),(2,80000,150000,0.0325,20),(3,100000,180000,0.0325,10),(4,500000,800000,0.0325,50),(5,150000,300000,0.0325,30);
/*!40000 ALTER TABLE `FundUser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `User` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary Key',
  `name` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `credit` int DEFAULT NULL,
  `salary` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10004 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `User`
--

LOCK TABLES `User` WRITE;
/*!40000 ALTER TABLE `User` DISABLE KEYS */;
INSERT INTO `User` VALUES (1,'xiaoming','123456',1,10000),(2,'xiaozhang','123456',0,8000),(3,'xiaoxu','123456',1,3000),(4,'xiaofang','123456',1,30000),(5,'xiaochen','123456',1,12000),(10000,'fundadmin','100000',NULL,NULL),(10001,'bankadmin1','100001',NULL,NULL),(10002,'bankadmin2','100002',NULL,NULL),(10003,'bankadmin3','100003',NULL,NULL);
/*!40000 ALTER TABLE `User` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-25 14:59:31
