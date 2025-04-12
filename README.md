Brief DescriptionA web-based software application designed to import, read, and manage preformatted XLSX and CSV files containing customer data. The application provides an elegant user interface, enabling managers to oversee sales assistants while restricting data access based on user roles. Sales staff can update customer status while managers can monitor overall activity, making customer management efficient and organized.
Features  

User Authentication: Enable secure sign-up and login for managers and sales users with role-based access control.  
File Importing: Simple and effective functionality for uploading preformatted XLSX and CSV files to the database.  
Dashboard Interface: Intuitive dashboards for managers and sales staff displaying relevant metrics and statuses.  
Dynamic Data Access: Role-based access allows users to view only the data assigned to them.  
Status Management: Sales users can set customer status from predefined options (CALLED, NOT ANSWERED, INVALID NUMBER, PLAN PRESENTED, SHORTLISTED) using an enum.

User Flow  

Users land on the login page and authenticate using their credentials.  
Upon successful login, users are directed to their respective dashboards.  
Managers can upload CSV/XLSX files to the system, view all assigned data, and monitor user interactions.  
Sales staff can view their specific data records and update customer statuses as needed.  
Both roles can navigate through the sidebar to access different functionalities, such as data overview, import history, and user management.

Technical Stack  

Frontend: Django Template for rendering dynamic webpages, styled with Tailwind CSS for an elegant user interface.  
Backend: Django for server-side logic, data processing, and user management.  
Database: SQLite for lightweight and efficient data storage.

Design Guidelines  

Styling Guidelines: Utilize a modern color palette to offer an elegant aesthetic; ensure typography is clean and readable; incorporate responsive UI components.  
Page Layout: Organize elements with a clear hierarchy; the dashboard should feature key metrics prominently, and the sidebar navigation should be easily accessible.  
Navigation Structure: Use a collapsible sidebar to organize key features, including Data Overview, Import History, and User Management.

Backend Structure  

Database Architecture: Design a schema that accommodates user roles, customer data (name, phone number, etc.), and status updates.  
API Endpoints: 
POST /upload for uploading files.  
GET /dashboard for fetching data tailored to user roles.  
PUT /status for updating customer status.


Security Measures: Implement user role validation to protect sensitive data, incorporating appropriate authentication and authorization protocols.

In-Scope and Out-of-Scope ItemsIn-Scope:  

Core features outlined above, including importing CSV/XLSX files, role-based dashboards, and status management.Out-of-Scope:  
Advanced analytics beyond basic activity monitoring.  
Integration with external systems for additional data sources or CRM tools.

