"""Cookbook client for the api where users can create and store recipes."""

import json
import requests

from pick import pick

API_URL = "http://127.0.0.1:5000"

def add_user(href):
    """Add a user in the client."""
    body = {}
    while True:
        print("Give name for user: ")
        body["name"] = input()
        if not body["name"]:
            continue
        print("Give email for user: ")
        body["email"] = input()
        if not body["email"]:
            continue
        print("Give address for user: ")
        body["address"] = input()
        if not body["address"]:
            continue
        print("Give password for user: ")
        body["password"] = input()
        if not body["password"]:
            continue
        print("-------------------------\n")
        return requests.post(API_URL + href, data=json.dumps(body),
                            headers={"Content-type": "application/json"}
        )


def list_users(href):
    """List all users from API."""
    resp = requests.get(API_URL + href)
    body = resp.json()
    for item in body["items"]:
        print("name: "+str(item["name"]))
        print("email: "+str(item["email"]))
        print("address: "+str(item["address"]))
        print("-------------------------\n")
    input("press ENTER to exit\n")

def delete_user(href):
    """Delete given user from API."""
    return requests.delete(API_URL + href[1])

def select_user(href):
    """Select the user for recipes."""
    while True:
        title = "Select a user"
        resp = requests.get(API_URL + href)
        body = resp.json()
        options = [item["name"] for item in body["items"]]
        options.append("cancel")
        option, _ = pick(options, title)
        if option == "cancel":
            return None
        if option:
            for i in body["items"]:
                if option in i["name"]:
                    name = option
                    href = i["@controls"]["self"]["href"]
            return name, href

def all_recipes(href, name):
    """List all recipes of the user."""
    resp = requests.get(API_URL + href)
    body = resp.json()
    if len(body["items"]) == 0:
        input(f"User-{name} has no recipes\n-------------------------\npress ENTER to exit\n")
        return
    for item in body["items"]:
        print("name: "+str(item["name"]))
        print("difficulty: "+str(item["difficulty"]))
        print("-------------------------\n")
    input("press ENTER to exit\n")
    return

def add_recipe(href):
    """Add a new recipe for the user."""
    body = {"recipe": {}}
    while True:
        body["recipe"]["name"] = input("Give name for recipe: ")
        if not body["recipe"]["name"]:
            continue
        body["recipe"]["description"] = input("Give description for recipe: ")
        if not body["recipe"]["description"]:
            continue
        body["recipe"]["difficulty"] = input("Give difficulty for recipe (easy, medium, hard): ")
        if not body["recipe"]["difficulty"]:
            continue
        try:
            amount = int(input("How many ingredients the recipe has?: "))
        except ValueError:
            print("Amount must be integer!")
            continue
        ingredients = []
        for _ in range(amount):
            data = {}
            data["name"] = input("Give ingredient name: ")
            data["unit"] = input("Give an unit of measurement (e.g. ml, dl, cup): ")
            data["amount"] = int(input("Give the amount (integer): "))
            ingredients.append(data)
        body["ingredients"] = ingredients
        print("-------------------------\n")
        return requests.post(API_URL + href, data=json.dumps(body),
                            headers={"Content-type": "application/json"}
        )

def select_recipe(href):
    """Select the recipe."""
    while True:
        title = "Select a recipe"
        resp = requests.get(API_URL + href)
        body = resp.json()
        options = [item["name"] for item in body["items"]]
        options.append("cancel")
        option, _ = pick(options, title)
        if option == "cancel":
            return None
        title = "Choose action"
        if option:
            for i in body["items"]:
                if option in i["name"]:
                    href = i["@controls"]["self"]["href"]
            return href

def get_recipe(href):
    """Gets the chosen recipe."""
    resp = requests.get(API_URL + href)
    body = resp.json()
    print("name: "+str(body["name"]))
    print("description: "+str(body["description"]))
    print("difficulty: "+str(body["difficulty"]))
    print("\ningredients:\n")
    for i, _ in enumerate(body["ingredients"]["items"]):
        print("    "+body["ingredients"]["items"][i]["name"],
         body["ingredients"]["items"][i]["amount"],
         body["ingredients"]["items"][i]["unit"])
    print("-------------------------\n")
    input("press ENTER to exit\n")


def delete_recipe(href):
    """Delete given user from API."""
    return requests.delete(API_URL + href)

def recipe_menu(name):
    """Show menu for user where you can do recipe-actions."""
    recipes_href = requests.get(API_URL + name[1]).json()["@controls"]["user-recipes"]["href"]
    while True:
        title = f"{name[0]}'s cookbook"
        options = ["Add recipe", "List all recipes", "Inspect recipe", "Delete recipe", "Exit"]
        option, _ = pick(options, title)

        title = "Choose action"
        if option == "Add recipe":
            add_recipe(recipes_href)
        if option == "List all recipes":
            all_recipes(recipes_href, name[0])
        if option == "Inspect recipe":
            recipe_href = select_recipe(recipes_href)
            if recipe_href is None:
                input("No recipe selected!\npress ENTER to exit\n")
                continue
            get_recipe(recipe_href)
        if option == "Delete recipe":
            recipe_href = select_recipe(recipes_href)
            if recipe_href is None:
                input("No recipe selected!\npress ENTER to exit\n")
                continue
            delete_recipe(recipe_href)
        elif option == "Exit":
            return

def main():
    """Loop the main menu."""
    ###LOANED FROM LOVELACE EXEC 4 EXAMPE(how client starts interaction with API)###
    ###, https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/###
    with requests.Session() as ses:
        ses.headers.update({"Accept": "application/vnd.mason+json"})
        resp = ses.get(API_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API")
        else:
            body = resp.json()
            users_href = body["@controls"]["cookbook:users-all"]["href"]
    ###
    while True:
        title = "Select user to examine its cookbook,\
you can also create new users and delete or check existing users."
        options = ["User creation", "User selection", "User deletion", "List users", "Exit"]
        option, _ = pick(options, title)
        title = "Choose action"
        if option == "User creation":
            add_user(users_href)
        elif option == "User selection":
            name = select_user(users_href)
            if name is None:
                input("No user selected!\npress ENTER to exit\n")
                continue
            recipe_menu(name)
        elif option == "List users":
            list_users(users_href)
        elif option == "User deletion":
            name = select_user(users_href)
            if name is None:
                input("No user selected!\npress ENTER to exit\n")
                continue
            delete_user(name)
        elif option == "Exit":
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")
