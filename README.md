# Article App with Flask

This is an python CMS made with flask. With it you can show your articles, post new ones, edit and delete existing ones.

To use it you have to have MySQL on your system and make two tables:

```
CREATE TABLE users(id INT(11) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), username VARCHAR(30), password VARCHAR(100), register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
```

```
CREATE TABLE articles (id INT(11) AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), author VARCHAR(100), body text, create_date tiMESTAMP DEFAULT CURRENT_TIMESTAMP);
```

After that run command:

### python app.py

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/SekeNikola/flexy/graphs/commit-activity)
[![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](https://github.com/SekeNikola/article-app-with-flesk)
![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
