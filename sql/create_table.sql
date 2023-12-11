-- user表
create table User(user_id int primary key, user_name varchar(255) not null, password varchar(255) not null);

-- company表
-- company_type: 航空公司、酒店、租车公司、景点管理公司
create table Company(company_id int primary key, company_name varchar(255) not null, company_type varchar(255) not null, password varchar(255) not null);

-- info表
-- flightInfo
create table FlightInfo(flight_id int primary key, departure_city varchar(255) not null, arrival_city varchar(255) not null, departure_time DATE not null, price decimal(10, 2) not null,company_id int, foreign key(company_id) references Company(company_id));

-- hotel
create table Hotel(hotel_id int primary key, hotel_name varchar(255) not null, city varchar(255) not null, company_id int, foreign key(company_id) references Company(company_id));

-- roomInfo
create table RoomInfo(room_id int primary key, room_number varchar(255) not null, room_type varchar(255) not null, room_price decimal(10, 2), hotel_id int, foreign key(hotel_id) references Hotel(hotel_id));

-- rent car
create table CarRental(carrental_id int primary key, car_type varchar(255) not null, transmission_type varchar(255) not null, rental_location varchar(255), return_location varchar(255), company_id int, foreign key (company_id) references Company(company_id) );

-- 景点
CREATE TABLE Attraction (attraction_id int PRIMARY KEY, attraction_name VARCHAR(255), city varchar(255), company_id INT, FOREIGN KEY (company_id) REFERENCES Company(company_id) );

-- 导游
CREATE TABLE Guide ( guide_id INT PRIMARY KEY, guide_name VARCHAR(255), guide_phone VARCHAR(255), attraction_id INT, FOREIGN KEY (attraction_id) REFERENCES Attraction(attraction_id));