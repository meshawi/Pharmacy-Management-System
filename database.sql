SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `orderitems` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `order_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` varchar(50) DEFAULT 'Pending',
  `total_amount` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock_quantity` int(11) NOT NULL,
  `category` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `products` (`id`, `name`, `description`, `price`, `stock_quantity`, `category`) VALUES
(1, 'Aspirin', 'Pain reliever and fever reducer', 5.00, 100, 'Pain Relief'),
(2, 'Paracetamol', 'Commonly used for mild pain and fever', 3.50, 200, 'Pain Relief'),
(3, 'Ibuprofen', 'Non-steroidal anti-inflammatory drug', 7.00, 150, 'Pain Relief'),
(4, 'Cetirizine', 'Used to treat hay fever and allergy symptoms', 8.00, 120, 'Allergy'),
(5, 'Loratadine', 'Antihistamine that reduces allergy symptoms', 6.50, 130, 'Allergy'),
(6, 'Insulin', 'Essential for managing blood sugar levels in diabetes', 45.00, 80, 'Diabetes Care'),
(7, 'Metformin', 'Helps control high blood sugar associated with type 2 diabetes', 20.00, 100, 'Diabetes Care'),
(8, 'Amoxicillin', 'Antibiotic used to treat a wide variety of bacterial infections', 12.00, 95, 'Antibiotics'),
(9, 'Doxycycline', 'Antibiotic used to treat bacterial infections, acne, and more', 18.00, 90, 'Antibiotics'),
(10, 'Multivitamins', 'Supplements containing various vitamins and minerals', 15.00, 300, 'Supplements'),
(11, 'Omega-3', 'Fish oil supplement beneficial for heart health', 25.00, 200, 'Supplements'),
(12, 'Calcium', 'Important for bone health and maintaining bone density', 10.00, 180, 'Supplements'),
(13, 'Cough Syrup', 'Provides relief from coughing and sore throat', 9.00, 110, 'Cold and Flu'),
(14, 'Nasal Spray', 'Helps relieve nasal congestion', 11.00, 85, 'Cold and Flu'),
(15, 'Thermometer', 'Digital device for measuring body temperature', 14.00, 60, 'Medical Devices');

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `review` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('Admin','Pharmacist','Customer') NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `users` (`id`, `username`, `email`, `password`, `role`, `first_name`, `last_name`, `date_of_birth`, `gender`, `phone_number`) VALUES
(1, 'Admin', 'testingAdmin@gmail.com', '79bd20ea6e92d08a24d0e659c9204e7e3ce6455715de0841a0bf28b9495c3671', 'Admin', 'Admin', 'ADMN', '2004-05-23', 'Male', '05555555555'),
(2, 'Pharmacist', 'testingpharmacist@gmail.com', 'c6ac26cd10d86956f695770dd004ee703f1ddbee15095fbf4c2e95b22421b262', 'Pharmacist', 'Pharm', 'Pharmacist', '2005-02-23', 'Male', '05666666666'),
(3, 'Customer', 'testingcustomer@gmail.com', '6353b03ffd0e7411e4e0c0093101eb869127c0339b05cf3a5cfd973f55d67ad0', 'Customer', 'Customer', 'CSTMR', '2006-05-23', 'Male', '05777777777');


ALTER TABLE `orderitems`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `product_id` (`product_id`);

ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`);

ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);


ALTER TABLE `orderitems`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;


ALTER TABLE `orderitems`
  ADD CONSTRAINT `orderitems_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `orderitems_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`);

ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
