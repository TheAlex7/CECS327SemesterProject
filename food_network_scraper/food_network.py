# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

# This script scrapes recipes specifically from the Food Network Website
import json
import jsonschema
import uuid
from jsonschema import validate

from bs4 import BeautifulSoup
import requests
import pymongo

def scrape_page(soup, recipe):
    # find all recipe links
    recipe_links = soup.find_all('li', class_='m-PromoList__a-ListItem')

    links_visited = set() # set to avoid revisiting already seen links
    try:
        with open("./data/visited_links.txt",'r') as visited_links:
            for line in visited_links:
                links_visited.add(line.strip())
    except FileNotFoundError:
        print("Creating visited_links.txt")
        with open("./data/visited_links.txt",'w') as _:
            pass
    

    # iterating through recipe link
    for link in recipe_links:
        recipe_url = 'https:' + link.find('a')['href']
        if recipe_url in links_visited:
            continue
        print(recipe_url)
        recipe_response = requests.get(recipe_url)
        recipe_html = recipe_response.text
        recipe_soup = BeautifulSoup(recipe_html, 'html.parser')

        #Extract recipe details
        recipe_name = recipe_soup.find('h1', class_ = 'o-AssetTitle__a-Headline').text.strip()
        ingredients_list = recipe_soup.find_all('p', class_ = 'o-Ingredients__a-Ingredient')
        ingredients = [ingredient.text.strip() for ingredient in ingredients_list]
        directions_list = recipe_soup.find_all('li', class_= 'o-Method__m-Step')
        directions = [direction.text.strip() for direction in directions_list]
        recipe.append(
            {
                'name': recipe_name.lower(),
                'ingredients': ingredients[1:],
                'instructions': directions,
                'source_url': recipe_url
            }
        
        )
        #newly seen link gets added to set and txt file
        links_visited.add(recipe_url)
        with open("./data/visited_links.txt",'a') as visited_links:
            visited_links.write(f"{recipe_url}\n")

def scrape_website():
    # the url of the home page of the target website
    base_url = 'https://www.foodnetwork.com/recipes/recipes-a-z'

    # defining the User-Agent header to use in the GET request below
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0)'
    }

    # retrieving the target web page
    page = requests.get(base_url, headers=headers)

    # parsing the target web page with Beautiful Soup
    soup = BeautifulSoup(page.text, 'html.parser')
    # initializing the variable that will contain
    # the list of all recipie data
    recipies = []

    # scraping the home page
    scrape_page(soup, recipies)

    # getting the "Next →" HTML element
    next_li_element = soup.find('a', class_='o-Pagination__a-Button.o-Pagination__a-NextButton')

    # if there is a next page to scrape
    while next_li_element is not None:

        check_next_page = soup.find_all('li', class_='o-Pagination__a-ListItem')

        if('o-Pagination__a-Button.o-Pagination__a-NextButton.is-Disabled' in check_next_page['class']):
            break

        next_page_relative_url = next_li_element.find('a', href=True)['href']
        
        # getting the new page
        page = requests.get(base_url + next_page_relative_url, headers=headers)

        # parsing the new page
        soup = BeautifulSoup(page.text, 'html.parser')

        # scraping the new page
        scrape_page(soup, recipies)

        # looking for the "Next →" HTML element in the new page
        next_li_element = soup.find('a', class_='o-Pagination__a-Button.o-Pagination__a-NextButton')

    #individual food recipe json schema
    with open('./data/food_recipe_schema.json', 'r') as schema_file:
        food_schema = json.load(schema_file)

    json_recipes = []
    for recipe in recipies:
        if isValid(recipe,food_schema):
            # writeToMongo(recipe)  ###UNCOMMENT THIS IF MONGO CONNECTIONS ARE SET UP
            uuid1 = str(uuid.uuid4()) # uuid for id of recipe object
            recipe["id"] = uuid1 # adding id to dictionary (recipe object)            
            # writeToJson(recipe)
            json_recipes.append(recipe)
            continue
        
    appendToJson("./data/food_network_recipes.json",json_recipes)
    print("Database loaded.")

# write json data objects to the mongoDB cloud server
def writeToMongo(data):
    res = collection.insert_one(data)
    return res

# function to add recipe entries to a json file
# NOTE: must pass in already validated data
def appendToJson(filename,data):
    # check if file exists, if not; reference an empty list
    try:
        with open(filename, "r") as json_file:
            current_file = json.load(json_file)
    except FileNotFoundError:
        current_file = []

    # combine new data with old data
    current_file.extend(data)

    # Replace old file with newly compiled data
    with open(filename, "w") as json_file:
        json.dump(current_file, json_file, indent=4)
    print("Data has been appended to", filename)

# function to write a recipe to its own json file
#  adds a new object ID field to the json object
# NOTE: must pass in already validated data
def writeToJson(data):
    uuid1 = data["id"] # id for filename
    #format the recipe name
    recipe_name = data["name"].replace(" ","_")
    recipe_name = recipe_name.replace("\"", "")
    # print(recipe_name)
    recipe_filename = f'{recipe_name}_{data["id"]}.json'

    # write recipe to it's own json file
    with open(f'./data/{recipe_filename}', 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f'Data has been successfully written to \'{recipe_filename}\'')

# function to validate data and ensure it is formatted correctly
def isValid(data, schema):
    valid = True
    try:
        validate(instance=data, schema=schema) 
    except jsonschema.exceptions.ValidationError as e:
        valid = False
        print("Data validation failed:", e)

    return valid

def main():
    scrape_website()

if __name__ == "__main__":
    ### connecting to mongo server
    ## MUST have proper connection string to write to mongo!!!
    client = pymongo.MongoClient("connection_string")
    db = client["RecipeDB"]
    collection = db["recipes"]
    ###

    main()
