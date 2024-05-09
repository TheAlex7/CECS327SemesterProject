# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

# This script scrapes recipes specifically from the Food Network Website
import sys
import os
import time
import json
import jsonschema
import uuid
from jsonschema import validate

from bs4 import BeautifulSoup
import requests

def scrape_page(soup, recipe):
    # find all recipe links
    recipe_links = soup.find_all('li', class_='m-PromoList__a-ListItem')

    links_visited = set() # set to avoid revisiting already seen links
    #load visited links
    with open("./food_network_scraper/visited_links.txt",'r') as visited_links:
        for line in visited_links:
            links_visited.add(line.strip())

    # iterating through recipe link
    for link in recipe_links:
        if link in links_visited:
            continue
        recipe_url = 'https:' + link.find('a')['href']
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
        # category_list = recipe_soup.find_all('a', class_= 'o-Capsule__a-Tag.a-Tag')
        # category = [category_list.soup.a['title'] for category in category_list] 
        # category = [category.text.strip() for category in category_list]
        recipe.append(
            {
                'name': recipe_name,
                'ingredients': ingredients[1:],
                'instructions': directions,
                'source_url': recipe_url
            }
        
        )
        #newly seen link gets added to set and txt file
        links_visited.add(link)
        with open("./food_network_scraper/visited_links.txt",'a') as visited_links:
            visited_links.write(f"{link}\n")

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
    
    #schema to compile multiple recipes into 1 json file.
    # this json file will be labeled according to the main domain source
    # of the recipes
    with open('./data/website_specific_recipes_schema.json', 'r') as schema_file:
        website_schema = json.load(schema_file)

    json_recipes = []
    for recipe in recipies:
        uuid1 = str(uuid.uuid4()) # uuid for id of recipe object
        recipe["id"] = uuid1 # adding id to dictionary (recipe object)
        json_recipes.append(recipe)
        # writetojson(recipe,food_schema)

    # convert list of individual recipes into dict
    data = {"recipes":json_recipes}
    appendToJson("./data/food_network_recipes.json",data,website_schema)

# function to add recipe entries to a json file
def appendToJson(filename,data, schema):
    # check if file exists, if not; reference an empty list
    try:
        with open(filename, "r") as json_file:
            current_file = json.load(json_file)
    except FileNotFoundError:
        current_file = []

    #validate to ensure data is formatted correctly
    try:
        validate(instance=data, schema=schema) 
    except jsonschema.exceptions.ValidationError as e:
        print("Data validation failed:", e)
    else:
        # Append new data to old data
        current_file.append(data)

        # Replace old file with newly compiled data
        with open(filename, "w") as json_file:
            json.dump(current_file, json_file, indent=4)
        print("Data has been appended to", filename)

# function to write a recipe to its own json file
def writetojson(data, schema):
    #format the recipe name
    recipe_name = data["name"].replace(" ","_")
    recipe_name = recipe_name.replace("\"", "")
    # print(recipe_name)
    recipe_filename = f'{recipe_name}_{data["id"]}.json'

    # validate data
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        print("Data validation failed:", e)
    else:
        with open(f'./data/{recipe_filename}', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f'Data has been successfully written to \'{recipe_filename}\'')

def main():
    # Load JSON Schema
    # with open('./data/food_recipe_schema.json', 'r') as schema_file:
    #     schema = json.load(schema_file)
        
    # Retrieve NODE_ID environment variable to identify the node
    node_id = os.getenv('NODE_ID')
    print(f'STARTING UP NODE {node_id}')

    scrape_website()

if __name__ == "__main__":
    main()
