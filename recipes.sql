CREATE TABLE Users(id SERIAL PRIMARY KEY, username TEXT, password TEXT, admin BOOLEAN, timestamp TIMESTAMP);
CREATE TABLE Recipes(id SERIAL PRIMARY KEY, name TEXT, user_id INTEGER REFERENCES Users (id), difficulty INTEGER, active_time INTEGER, passive_time INTEGER, meal_type TEXT, timestamp TIMESTAMP);
CREATE TABLE Ingredients (id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id),name TEXT, amount TEXT);
CREATE TABLE Instructions (id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id), text TEXT);

CREATE TABLE Comments(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES Users (id), recipe_id INTEGER REFERENCES Recipes (id), text TEXT, date DATE);
