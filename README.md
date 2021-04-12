README.md

Trello board for project management can be found here:
https://trello.com/b/QnpZosBC/leaky-flask


Navigate to:
http://3.88.53.207:4000/

There are two cowrking challenges: SQL injection and Server Side Template Injection.

The SQL injection challenge requires an authorisation bypass to login as the admin users. Upon successfully loging in, you will then be taken to a new level with some SQL characters blacklisted, making the challenge harder. There are a number of levels to complete.

The Server Side Template challenge is simply a sandbox environment to play with potential attacks. There are no levels here, and you may simply enter the payloads as you wish.

If you are unsure what to do you can find some suggestions here:
https://github.com/swisskyrepo/PayloadsAllTheThings


List of dependencies:
click>=7.1.2
Flask>=1.1.2
itsdangerous>=1.1.0
Jinja2>=2.11.2
lxml>=4.5.2
MarkupSafe>=1.1.1
pycryptodome>=3.9.8
Werkzeug>=1.0.1
Flask-Migrate>=2.0.2
