# plannter

A web application, allowing the user to select plants to be grown, in order to see a summary of work to be done at a particular time. The application allows the user to configure weekly mail reminders on the work to be done in the garden.

This web application was created as the final project of the CS50x course. The distribution code for pset9 was used as a starting point (see https://cs50.harvard.edu/x/2022/psets/9/finance/).

## Instructions for use

The application allows the user to configure a garden by selecting a number of plants to be grown in a growing season.

### Video Demo
https://www.youtube.com/watch?v=FqpLhn4o35E

### User Registration and Login
Create an account by clicking on the register button and selecting a username, providing an e-mail and inputting and confirming a password. After a successful login, the user is presented by an empty home screen. In order to see the activities on the selected plants, they must be selected on the Planner page.
The user password can be changed once the user is logged in by selecting the option from the dropdown menu on the username.

### Garden Configuration (Planner page)
The Planner page shows all the plants, present in the Plannter database, with an overview of activities throughout the year. The user can select multiple plans and save them in order to see the overview of the activities on the homepage.

### Weekly View and Mail Notifications (Weekly page)
Once the user configured a set of plants in the Planner page, the activities for the particular week are displayed for the selected plants on the Weekly page. For each activity on the garden, the subset of plants are displayed. The user can also send a copy of the weekly summary to all the mails, defined in the user settings.

### Modify Settings (Settings page)
On the settings page, the user can modify the following:
- Mail notifications: The Plannter application sends the weekly summary on specified days at 20:00 CET.
- E-mail(s): Multiple e-mails can be defined for the mail notifications (up to 5).
- Plant name language: English and Slovenian is available for the plant names and activities in the Planner, Weekly and Mail Notifications.

## Application description

### Backend
The Plannter application uses Flask as the web framework. In addition, the following notable libraries are used:
- cs50 for the SQL database
- flask_session for user sessions
- flask_mail for sending e-mails from the application
- flask_babel for translation of web and mail HTML
- apscheduler for scheduling weekly notification mails

The core of the application is implemented in app.py, which contains the python backend for processing the GET and POST requests from the clients, mainly connected to writing and reading into the database and related data processing
The database is split into the following tables:
- users (id, username, hash)
- plants (id, user_id, name_si, name_en, todo_*_*): this table is prepared for a future feature expansion, as it stores the user_id which created the plants. The default plants are created by an admin account, but as a future expansion, users will be able to modify the default and create new plants. As the changes should be localized to a single user, they need to be tracked to his/her user_id.
- selected_plants (user_id, selected_plants): selected plants are stored as a comma-separated string of the plant ids that the user selected
- settings (user_id, emails, notifications, language): emails and notifications are stored as a comma-separated string.

Configuration of the flask plugins and some configuration constants are separated into a config.py
helpers/helpers.py contains the supporting functions, called from the app.py application.

### Frontend
HTML, CSS (Bootstrap) and JavaScript are used on the front-end, with Jinja2 as the templating tool.
The HTML pages are stored in the templates folder, separated out into pages, extending the basic layout.html
JavaScript is used on the settings page to dynamically change the number of e-mail fields.
Translation files for Slovenian language are stored in the translation folder and passed to the front-end by the flask_babel plugin.

### Deployment
The application is deployed on the Heroku servers using the PostgreSQL database.

