from . import models
from . import db
from sqlite3 import IntegrityError

def populate_db():
    new_user = models.User(
                name="Taneli-Testiukko",
                email="testi.testi@testi.com",
                password="EeppinenPassuJokaonTurvallinen"
            )

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        print("Database already has user added for this test")

    ing1 = models.Ingredient(name="Egg")
    ing2 = models.Ingredient(name="Salt")
    ing3 = models.Ingredient(name="Sugar")
    ing4 = models.Ingredient(name="Milk")
    ing5 = models.Ingredient(name="Flour")
    ing6 = models.Ingredient(name="Water")

    db.session.add_all([ing1, ing2, ing3, ing4, ing5, ing6])
    db.session.commit()

    meas1 = models.Unit(unit="Cup")
    meas2 = models.Unit(unit="Teaspoon")
    meas3 = models.Unit(unit="pcs")

    db.session.add_all([meas1, meas2, meas3])
    db.session.commit()

    recipe1 = models.Recipe(
                name = "Cake-Recipe",
                description = "Lisaa vahan jauhoja eheheh",
                user_id=new_user.id)

    recipe2 = models.Recipe(
                name = "Water-Recipe",
                description = "Avaa hana ja laita lasi alle",
                user_id=new_user.id)

    ingredients_1 = [[ing1, 2, meas3], [ing2, 1, meas2], [ing6, 1, meas1], [ing3, 4, meas2]]
    ingredients_2 = [[ing6, 1, meas1]]

    db.session.add_all([recipe1, recipe2])
    db.session.commit()

    for ingredient in ingredients_1:
        new_ingredients = models.Recipeingredient(
            id = recipe2.id,
            ingredient_id = ingredient[0].id,
            amount = ingredient[1],
            unit_id = ingredient[2].id
        )
        db.session.add(new_ingredients)
        db.session.commit()

    for ingredient in ingredients_2:
        new_ingredients = models.Recipeingredient(
            id = recipe1.id,
            ingredient_id = ingredient[0].id,
            amount = ingredient[1],
            unit_id = ingredient[2].id
        )
        db.session.add(new_ingredients)
        db.session.commit()
    
def get_db():    

    resepti = db.session.query(
            models.Recipe.name,
            models.Ingredient.name,
            models.Recipeingredient.amount,
            models.Unit.unit
            ).filter(
                models.Ingredient.id == models.Recipeingredient.ingredient_id
            ).filter(
                models.Recipeingredient.id == models.Recipe.id
            ).filter(
                models.Unit.id == models.Recipeingredient.unit_id
            ).all()

    for row in resepti:
        print(row)

    print()
    print("Recipes: ")

    for row in db.session.query(models.Recipe.name, models.Recipe.description).all():
        print(row)
    print()

    print("Ingredients: ")

    for row in db.session.query(models.Ingredient.name).all():
        print(row)
    print()

    print("Users: ")

    for row in db.session.query(models.User.name).all():
        print(row)
    print()

    print("Units: ")

    for row in db.session.query(models.Unit.unit).all():
        print(row)
    print()