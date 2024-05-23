# Pharmacy Management System

#### Video Demo: [URL HERE]

#### Description:

## Introduction

Hello everyone, my name is Mohammed Aleshawi. This is my final project for CS50. The Pharmacy Management System is a web-based application designed to help manage various aspects of a pharmacy. This includes user management, product inventory, order processing, and reporting. The project leverages technologies such as Flask for the backend, HTML, CSS, and JavaScript for the frontend, and MySQL for the database.

## Project Structure

The project is organized into several key files and directories:

- `app.py`: The main Flask application file that initializes the app and defines the routes.
- `templates/`: Contains all the HTML templates used in the project, including base layout and specific pages like login, register, dashboard, etc.
- `static/`: Contains static files like CSS, JavaScript, images, and animations.
- `database.sql`: SQL file used to create the necessary database schema.
- `README.md`: This file, providing an overview and documentation of the project.

## Features

### User Management

- **Registration and Login**: Users can register and log in with their username, email, and password. The system supports role-based access control (Admin, Pharmacist, Customer).
- **Edit Account**: Users can edit their account details including username, email, password, and personal information.
- **Reset Password**: Users can reset their password by providing their username and either their email or phone number.

### Product Management

- **View Products**: All users can view the list of available products, along with their details like name, description, price, and stock quantity.
- **Add/Edit Products**: Admins can add new products and edit existing ones, specifying details such as name, description, price, stock quantity, and category.
- **Delete Products**: Admins can delete products, provided they are not referenced in any orders.

### Order Management

- **Cart**: Customers can add products to their cart, view the cart, and remove items from it.
- **Order Placement**: Customers can confirm orders, which updates the product inventory and creates an order record.
- **Order History**: Customers can view their past orders, including the details of each order.

### Reviewing and Rating System

- **Submit Review and Rating**: After confirming an order, customers can rate and review the products they purchased.
- **View Reviews and Ratings**: All users can view the reviews and ratings for each product, helping them make informed purchasing decisions.

### Reporting and Analytics

- **Sales Report**: Admins can view sales data, including total sales and number of orders over a specified period.
- **Inventory Report**: Admins can view inventory status, including total products sold and current stock levels.

### Additional Features

- **Contact Information**: The website provides contact information for the developer, including links to the portfolio and social media profiles.

## Design Choices

Several design choices were made during the development of this project:

1. **Role-Based Access Control**: Implementing different roles (Admin, Pharmacist, Customer) ensures that only authorized users can perform specific actions, enhancing security and usability.
2. **Responsive Design**: The front end is built using Bootstrap to ensure the application is responsive and works well on various devices.
3. **Modular Code Structure**: The project is organized into clear, modular files and directories, making it easier to maintain and extend.

## Challenges and Solutions

Throughout the development of this project, several challenges were encountered and addressed:

- **Database Design**: Designing the database schema to efficiently handle user data, product inventory, and order records was critical. Careful planning and normalization techniques were used to optimize performance.
- **Authentication and Security**: Implementing secure authentication mechanisms, including password hashing and session management, to protect user data.
- **User Interface**: Ensuring a user-friendly interface that allows easy navigation and interaction with the system.

## Tools and Resources

For this project, I heavily relied on various documentation and resources available on the web:

- **W3Schools**: For general HTML, CSS, JavaScript, and SQL reference.
- **Stack Overflow**: For troubleshooting and solving errors.
- **ChatGPT**: For assistance with complex parts and to enhance the Bootstrap design.
- **CS50 Lectures**: For foundational knowledge and guidance on using Flask and other technologies.

## Code Details

For more in-depth information about the code structure and functionality, please refer to the [Code Details Document](CODE_DETAILS.md).

## Conclusion

The Pharmacy Management System project showcases the application of various web development technologies and concepts learned during the CS50 course. It provides a comprehensive solution for managing a pharmacy's operations, including user management, product inventory, order processing, and reporting. This project highlights the importance of careful planning, modular design, and attention to detail in software development.

Feel free to check out the video demo for a detailed walkthrough of the project's features and functionality: [Video Demo URL HERE].

---

Thank you for reviewing my final project. **This was CS50!**
