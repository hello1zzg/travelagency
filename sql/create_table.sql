-- 1. 删除现有触发器和表（如果需要）
DROP TRIGGER IF EXISTS trg_Rating_AFTER_INSERT;
DROP TRIGGER IF EXISTS trg_Rating_AFTER_UPDATE;
DROP TRIGGER IF EXISTS trg_FlightInfo_AFTER_INSERT;
DROP TRIGGER IF EXISTS trg_Hotel_AFTER_INSERT;
DROP TRIGGER IF EXISTS trg_CarRental_AFTER_INSERT;
DROP TRIGGER IF EXISTS trg_Attraction_AFTER_INSERT;
DROP TRIGGER IF EXISTS trg_Guide_AFTER_INSERT;
DROP TRIGGER IF EXISTS trg_UserRating_AFTER_INSERT;


DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS UserRating;
DROP TABLE IF EXISTS Rating;
DROP TABLE IF EXISTS AtrrGuide;
DROP TABLE IF EXISTS Guide;
DROP TABLE IF EXISTS Attraction;
DROP TABLE IF EXISTS CarRental;
DROP TABLE IF EXISTS RoomInfo;
DROP TABLE IF EXISTS Hotel;
DROP TABLE IF EXISTS FlightInfo;
DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS User;

-- 2. 创建表结构

-- User 表
CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL DEFAULT 'user'
);

-- Company 表
CREATE TABLE Company (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- FlightInfo 表
CREATE TABLE FlightInfo (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    departure_city VARCHAR(255) NOT NULL,
    arrival_city VARCHAR(255) NOT NULL,
    departure_time DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    rating FLOAT NOT NULL,
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);

-- Hotel 表
CREATE TABLE Hotel (
    hotel_id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    rating FLOAT NOT NULL,
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);

-- RoomInfo 表
CREATE TABLE RoomInfo (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(255) NOT NULL,
    room_type VARCHAR(255) NOT NULL,
    room_price DECIMAL(10, 2),
    hotel_id INT,
    FOREIGN KEY (hotel_id) REFERENCES Hotel(hotel_id)
);

-- CarRental 表
CREATE TABLE CarRental (
    carrental_id INT PRIMARY KEY AUTO_INCREMENT,
    car_type VARCHAR(255) NOT NULL,
    transmission_type VARCHAR(255) NOT NULL,
    rental_location VARCHAR(255),
    return_location VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    rating FLOAT NOT NULL,
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);

-- Attraction 表
CREATE TABLE Attraction (
    attraction_id INT PRIMARY KEY AUTO_INCREMENT,
    attraction_name VARCHAR(255),
    city VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    rating FLOAT NOT NULL,
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);

-- Guide 表
CREATE TABLE Guide (
    guide_id INT PRIMARY KEY AUTO_INCREMENT,
    guide_name VARCHAR(255),
    guide_phone VARCHAR(255),
    price DECIMAL(10, 2) NOT NULL,
    rating FLOAT NOT NULL
);

-- AtrrGuide 表
CREATE TABLE AtrrGuide (
    guide_id INT,
    attraction_id INT,
    PRIMARY KEY (guide_id, attraction_id),
    FOREIGN KEY (attraction_id) REFERENCES Attraction(attraction_id),
    FOREIGN KEY (guide_id) REFERENCES Guide(guide_id)
);

-- Rating 表
CREATE TABLE Rating (
    rating_id INT PRIMARY KEY AUTO_INCREMENT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    total_rating DECIMAL(10,2) NOT NULL,
    count INT NOT NULL,
    avg_rating DECIMAL(10,2) NOT NULL,
    UNIQUE (entity_type, entity_id)
);

-- 创建 UserRating 表（不包含 user_id 列）
CREATE TABLE UserRating (
    user_rating_id INT PRIMARY KEY AUTO_INCREMENT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NOT NULL,
    rating DECIMAL(10,2) NOT NULL
);

-- 3. 插入现有实体表的数据到 Rating 表
-- 如果表中已有数据，可以执行以下插入语句

INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
SELECT 'FlightInfo', flight_id, rating, 1, rating FROM FlightInfo;

INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
SELECT 'Hotel', hotel_id, rating, 1, rating FROM Hotel;

INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
SELECT 'CarRental', carrental_id, rating, 1, rating FROM CarRental;

INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
SELECT 'Attraction', attraction_id, rating, 1, rating FROM Attraction;

INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
SELECT 'Guide', guide_id, rating, 1, rating FROM Guide;

-- 4. 创建实体表的 AFTER INSERT 触发器

DELIMITER //

-- FlightInfo AFTER INSERT Trigger
CREATE TRIGGER trg_FlightInfo_AFTER_INSERT
AFTER INSERT ON FlightInfo
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
        VALUES ('FlightInfo', NEW.flight_id, NEW.rating, 1, NEW.rating);
        SET @trg_flag = NULL;
    END IF;
END;
//

-- Hotel AFTER INSERT Trigger
CREATE TRIGGER trg_Hotel_AFTER_INSERT
AFTER INSERT ON Hotel
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
        VALUES ('Hotel', NEW.hotel_id, NEW.rating, 1, NEW.rating);
        SET @trg_flag = NULL;
    END IF;
END;
//

-- CarRental AFTER INSERT Trigger
CREATE TRIGGER trg_CarRental_AFTER_INSERT
AFTER INSERT ON CarRental
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
        VALUES ('CarRental', NEW.carrental_id, NEW.rating, 1, NEW.rating);
        SET @trg_flag = NULL;
    END IF;
END;
//

-- Attraction AFTER INSERT Trigger
CREATE TRIGGER trg_Attraction_AFTER_INSERT
AFTER INSERT ON Attraction
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
        VALUES ('Attraction', NEW.attraction_id, NEW.rating, 1, NEW.rating);
        SET @trg_flag = NULL;
    END IF;
END;
//

-- Guide AFTER INSERT Trigger
CREATE TRIGGER trg_Guide_AFTER_INSERT
AFTER INSERT ON Guide
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
        VALUES ('Guide', NEW.guide_id, NEW.rating, 1, NEW.rating);
        SET @trg_flag = NULL;
    END IF;
END;
//

DELIMITER ;

-- 5. 创建 Rating 表的 AFTER INSERT 和 AFTER UPDATE 触发器

DELIMITER //

-- Rating AFTER INSERT Trigger
CREATE TRIGGER trg_Rating_AFTER_INSERT
AFTER INSERT ON Rating
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        IF NEW.entity_type = 'FlightInfo' THEN
            UPDATE FlightInfo SET rating = NEW.avg_rating WHERE flight_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'Hotel' THEN
            UPDATE Hotel SET rating = NEW.avg_rating WHERE hotel_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'CarRental' THEN
            UPDATE CarRental SET rating = NEW.avg_rating WHERE carrental_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'Attraction' THEN
            UPDATE Attraction SET rating = NEW.avg_rating WHERE attraction_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'Guide' THEN
            UPDATE Guide SET rating = NEW.avg_rating WHERE guide_id = NEW.entity_id;
        END IF;
        SET @trg_flag = NULL;
    END IF;
END;
//

-- Rating AFTER UPDATE Trigger
CREATE TRIGGER trg_Rating_AFTER_UPDATE
AFTER UPDATE ON Rating
FOR EACH ROW
BEGIN
    IF @trg_flag IS NULL THEN
        SET @trg_flag = 1;
        IF NEW.entity_type = 'FlightInfo' THEN
            UPDATE FlightInfo SET rating = NEW.avg_rating WHERE flight_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'Hotel' THEN
            UPDATE Hotel SET rating = NEW.avg_rating WHERE hotel_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'CarRental' THEN
            UPDATE CarRental SET rating = NEW.avg_rating WHERE carrental_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'Attraction' THEN
            UPDATE Attraction SET rating = NEW.avg_rating WHERE attraction_id = NEW.entity_id;
        ELSEIF NEW.entity_type = 'Guide' THEN
            UPDATE Guide SET rating = NEW.avg_rating WHERE guide_id = NEW.entity_id;
        END IF;
        SET @trg_flag = NULL;
    END IF;
END;
//

DELIMITER ;

-- 6. 创建 UserRating 表的 AFTER INSERT 触发器

DELIMITER //

CREATE TRIGGER trg_UserRating_AFTER_INSERT
AFTER INSERT ON UserRating
FOR EACH ROW
BEGIN
    -- 声明变量必须在 BEGIN 块的最前面
    DECLARE existing_total DECIMAL(10,2);
    DECLARE existing_count INT;
    DECLARE new_total DECIMAL(10,2);
    DECLARE new_avg DECIMAL(10,2);
    DECLARE no_row_found INT DEFAULT 0;

    -- 声明处理程序，用于捕捉未找到记录的情况
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET no_row_found = 1;

    -- 检查 Rating 表中是否已有记录
    SELECT total_rating, count INTO existing_total, existing_count
    FROM Rating
    WHERE entity_type = NEW.entity_type AND entity_id = NEW.entity_id
    FOR UPDATE;

    IF no_row_found = 0 THEN
        -- 计算新的总评分、计数和平均评分
        SET new_total = existing_total + NEW.rating;
        SET existing_count = existing_count + 1;
        SET new_avg = new_total / existing_count;

        -- 更新 Rating 表
        UPDATE Rating
        SET total_rating = new_total, count = existing_count, avg_rating = new_avg
        WHERE entity_type = NEW.entity_type AND entity_id = NEW.entity_id;
    ELSE
        -- 插入新的 Rating 记录
        INSERT INTO Rating (entity_type, entity_id, total_rating, count, avg_rating)
        VALUES (NEW.entity_type, NEW.entity_id, NEW.rating, 1, NEW.rating);
    END IF;

    -- 不需要设置 @trg_flag 在此处
END;
//

DELIMITER ;
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,                 -- 记录下单用户ID
    flight_id INT DEFAULT NULL,           -- 航班ID (可为空，表示不购票)
    hotel_id INT DEFAULT NULL,            -- 酒店ID (可为空)
    carrental_id INT DEFAULT NULL,        -- 租车ID (可为空)
    attraction_id INT DEFAULT NULL,       -- 景点ID (可为空)
    total_price DECIMAL(10,2) DEFAULT 0,  -- 总价格 (可根据业务需求计算或置0)
    status VARCHAR(50) DEFAULT 'pending', -- 订单状态 (pending, paid, canceled等)
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);