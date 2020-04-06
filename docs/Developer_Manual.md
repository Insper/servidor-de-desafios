# Developer Manual

This part of the documentation it's for those who want to contribute with new features,
documentation or correcting bugs on the application.

It's a short description of how the project was structured and which was the technologies
used for its construction.

## Technologies used

Here are the main stack elements used to built the application:

- Python
- SQL, SQLite3
- Flask
- Basic Auth
- HTML
- CSS
- Mkdocs
- Javascript

## Directory structure

One important to understand in a project when you want to contribute to it, it's to understand
where are each of the things in the project to start editing it. Let's take a look in the directory
structure below:

* documentation
    * docs
        * images
* src
    * static
    * templates
    * upload
* tests

Basically most of the files of the system that are going to be changed it's inside the src folder. 
The documentatios markdowns can be edited inside the documentation/docs.

## Lint

To check if the code you wrote it's in the expected format. You can run:

$ pylint <name_of_the_file>

We recommend a score of higher then 9.5 to be approved.


## Database

Before running the application you should prepare the database that the application
use. To do that you should have sqlite installed. If you haven't it you can run:

    $ pip install sqlite3

After that:

    $ sqlite

    $ .read quiz.sql

This will create the database for you.

## Running the application

To run the application you need to have all dependencies installed. The project does not
have a "requirements.txt" file yet. The main libraries required can be found in the top
of the softdes.py file. After installing them, run the main file:

    $ python softdes.py

Some seconds later you should have the server running on https://localhost:80

### Happy coding!