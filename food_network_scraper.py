from bs4 import BeautifulSoup
import requests
import csv

def scrape_page(soup, recipe):
    # find all recipe links
    recipe_links = soup.find_all('li', class_='m-PromoList__a-ListItem')

    # iterating through recipe link
    for link in recipe_links:
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
        category_list = recipe_soup.find_all('a', class_= 'o-Capsule__a-Tag.a-Tag')
        category = [category_list.soup.a['title'] for category in category_list] 
        # category = [category.text.strip() for category in category_list]
        recipe.append(
            {
                'name': recipe_name,
                'ingredients': ingredients,
                'directions': directions,
                'category': category
            }
        )

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


    # reading  the "quotes.csv" file and creating it
    # if not present
    csv_file = open('recipies.csv', 'w', encoding='utf-8', newline='')

    # initializing the writer object to insert data
    # in the CSV file
    writer = csv.writer(csv_file)

    # writing the header of the CSV file
    writer.writerow(['Name', 'Ingredients', 'Directions', 'Category'])

    # writing each row of the CSV
    for recipie in recipies:
        writer.writerow(recipie.values())

    # terminating the operation and releasing the resources
    csv_file.close()

def main():
    scrape_website()

main()