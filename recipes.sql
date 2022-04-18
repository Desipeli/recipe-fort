CREATE TABLE Users(id SERIAL PRIMARY KEY, username TEXT, password TEXT, admin BOOLEAN, date DATE);
CREATE TABLE Recipes(id SERIAL PRIMARY KEY, name TEXT, user_id INTEGER REFERENCES Users (id), difficulty INTEGER, active_time INTEGER, passive_time INTEGER, date DATE);
CREATE TABLE Ingredients (id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id),name TEXT, amount TEXT);
CREATE TABLE Instructions (id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id), text TEXT);

CREATE TABLE Comments(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES Users (id), recipe_id INTEGER REFERENCES Recipes (id), text TEXT, date DATE);
