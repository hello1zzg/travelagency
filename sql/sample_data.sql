-- company

INSERT INTO Company values
	(1, '南方航空', '航空公司', '123456'),
    (2, '东方航空', '航空公司', '123456'),
    (3, '四川航空', '航空公司', '123456'),
    (4, '山东航空', '航空公司', '123456');

INSERT INTO Company values
    (5, '维也纳酒店', '酒店', '123456'),
    (6, '汉庭酒店', '酒店', '123456'),
    (7, '如家酒店', '酒店', '123456');
    
INSERT INTO Company values
	(8, '神州租车', '租车公司', '123456'),
	(9, '至尊租车', '租车公司', '123456');
INSERT INTO Company values
	(10, '蜗牛景区管理', '景点管理公司', '123456'),
	(11, '黄山旅游公司', '景点管理公司', '123456');
	
-- user
INSERT INTO User values(1, '杨世明', '123456');

-- flight
INSERT INTO FlightInfo values
	(1, '北京', '成都', '2023-12-11', 1000, 4.5, 1),
	(2, '北京', '成都', '2023-12-11', 999, 5.0, 2),
	(3, '北京', '成都', '2023-12-11', 750, 4.2, 3);


-- hotel
-- create table Hotel(hotel_id int primary key, hotel_name varchar(255) not null, city varchar(255) not null, rating float not null, company_id int, foreign key(company_id) references Company(company_id));
INSERT INTO Hotel VALUES 
	(1, 'ABC酒店', '成都', 4.8, 5), 
	(2, 'DEF酒店', '成都', 4.2, 6),
	(3, 'XYZ酒店', '成都', 5.0, 7);

-- roomInfo
-- drop table if exists RoomInfo;
-- create table RoomInfo(room_id int primary key, room_number varchar(255) not null, room_type varchar(255) not null, room_price decimal(10, 2), hotel_id int, foreign key(hotel_id) references Hotel(hotel_id));

INSERT INTO RoomInfo VALUES 
	(1, '101', '单人间', 300.00, 1),
	(2, '201', '双人间', 500.00, 1),
	(3, '301', '双人间', 200.00, 2),
	(4, '401', '双人间', 600.00, 3);

-- rent car
-- drop table if exists CarRental;
-- create table CarRental(carrental_id int primary key, car_type varchar(255) not null, transmission_type varchar(255) not null, rental_location varchar(255), return_location varchar(255), price decimal(10, 2) not null, rating float not null, company_id int, foreign key (company_id) references Company(company_id) );

INSERT INTO CarRental VALUES
	(1, '中型车', '自动挡', '成都', '成都', 400.00, 4.5, 8), 
	(2, 'SUV', '手动挡', '成都', '成都', 800.00, 4.2, 8),
	(3, '微面', '手动挡', '成都', '成都', 300.00, 4.2, 9), 
	(4, '跑车', '自动挡', '成都', '成都', 1000.00, 4.7, 9),
	(5, '小型车', '自动挡', '成都', '成都', 350.00, 4.4, 8), 
	(6, 'SUV', '自动挡', '成都', '成都', 900.00, 4.6, 8),
	(7, '中型车', '自动挡', '成都', '成都', 500.00, 4.3, 9), 
	(8, '跑车', '自动挡', '成都', '成都', 1200.00, 4.8, 9);
-- 景点
drop table if exists Attraction;
CREATE TABLE Attraction (attraction_id int PRIMARY KEY, attraction_name VARCHAR(255), city varchar(255), price decimal(10, 2) not null, rating float not null, company_id INT, FOREIGN KEY (company_id) REFERENCES Company(company_id) );

INSERT INTO Attraction VALUES 
	(1, '锦里古街', '成都', 60.00, 4.7, 10), 
	(2, '宽窄巷子', '成都', 40.00, 4.5, 10), 
	(3, '都江堰', '成都', 80.00, 4.8, 11),
	(4, '武侯祠', '成都', 50.00, 4.6, 11);

 INSERT INTO Guide VALUES 
 	(1, '张导游', '13812345678', 200.00, 4.5),
	(2, '李导游', '13998765432', 180.00, 4.2), 
	(3, '王导游', '13654321789', 220.00, 4.6);

INSERT INTO AtrrGuide VALUES (1, 1), (1, 4), (2, 2), (2, 3), (3, 2), (3, 4);