CREATE TABLE Users(id SERIAL PRIMARY KEY, username TEXT, password TEXT, admin BOOLEAN, timestamp TIMESTAMP);
CREATE TABLE Recipes(id SERIAL PRIMARY KEY, name TEXT, user_id INTEGER REFERENCES Users (id) ON DELETE CASCADE, difficulty INTEGER, active_time INTEGER, passive_time INTEGER, meal_type TEXT, timestamp TIMESTAMP);
CREATE TABLE Ingredients (id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id) ON DELETE CASCADE, name TEXT, amount TEXT);
CREATE TABLE Instructions (id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id) ON DELETE CASCADE, text TEXT);

CREATE TABLE Likes ( id SERIAL PRIMARY KEY, recipe_id INTEGER REFERENCES Recipes (id) ON DELETE CASCADE, user_id INTEGER REFERENCES Users (id) ON DELETE CASCADE, liked BOOLEAN, timestamp TIMESTAMP);

CREATE TABLE Comments(id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES Users (id) ON DELETE CASCADE, recipe_id INTEGER REFERENCES Recipes (id) ON DELETE CASCADE, text TEXT, timestamp TIMESTAMP);
