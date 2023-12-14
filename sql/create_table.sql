-- user表
create table User(user_id int primary key, user_name varchar(255) not null, password varchar(255) not null);

-- company表
-- company_type: 航空公司、酒店、租车公司、景点管理公司
create table Company(company_id int primary key, company_name varchar(255) not null, company_type varchar(255) not null, password varchar(255) not null);

-- info表
-- flightInfo
drop table if exists FlightInfo;
create table FlightInfo(flight_id int primary key, departure_city varchar(255) not null, arrival_city varchar(255) not null, departure_time DATE not null, price decimal(10, 2) not null, rating float not null, company_id int, foreign key(company_id) references Company(company_id));

-- hotel
drop table if exists Hotel;
create table Hotel(hotel_id int primary key, hotel_name varchar(255) not null, city varchar(255) not null, rating float not null, company_id int, foreign key(company_id) references Company(company_id));

-- roomInfo
drop table if exists RoomInfo;
create table RoomInfo(room_id int primary key, room_number varchar(255) not null, room_type varchar(255) not null, room_price decimal(10, 2), hotel_id int, foreign key(hotel_id) references Hotel(hotel_id));

-- rent car
drop table if exists CarRental;
create table CarRental(carrental_id int primary key, car_type varchar(255) not null, transmission_type varchar(255) not null, rental_location varchar(255), return_location varchar(255), price decimal(10, 2) not null, rating float not null, company_id int, foreign key (company_id) references Company(company_id) );

-- 景点
drop table if exists Attraction;
CREATE TABLE Attraction (attraction_id int PRIMARY KEY, attraction_name VARCHAR(255), city varchar(255), price decimal(10, 2) not null, rating float not null, company_id INT, FOREIGN KEY (company_id) REFERENCES Company(company_id) );

-- 导游
drop table if exists Guide;
CREATE TABLE Guide (guide_id INT PRIMARY KEY, guide_name VARCHAR(255), guide_phone VARCHAR(255), price decimal(10, 2) not null, rating float not null);

-- 导游景点表
drop table if exists AtrrGuide;
CREATE TABLE AtrrGuide(guide_id INT, attraction_id INT, primary key(guide_id, attraction_id), foreign key(attraction_id) references Attraction(attraction_id), foreign key(guide_id) references Guide(guide_id));