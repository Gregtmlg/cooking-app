from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.models.ingredient import Ingredient
from app.models.recipe_ingredient import RecipeIngredient
from app.schemas.recipe import RecipeCreate, RecipeUpdate


def get_recipe(db : Session, recipe_id : int) -> Recipe | None: # Récupère une recette par son ID. Si la recette n'existe pas, retourne None.
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()

def get_recipes(db : Session, skip : int = 0, limit : int = 100) -> list[Recipe]:   # Récupère toutes les recettes avec pagination. Les paramètres skip et limit permettent de contrôler le nombre de recettes retournées et à partir de quel index commencer la récupération. Par défaut, il retourne les 100 premières recettes.
    return db.query(Recipe).offset(skip).limit(limit).all()

def create_recipe(db: Session, recipe_in: RecipeCreate) -> Recipe:
    db_recipe = Recipe(
        title=recipe_in.title,
        description=recipe_in.description,
        instructions=recipe_in.instructions,
        prep_time=recipe_in.prep_time,
        cook_time=recipe_in.cook_time,
        servings=recipe_in.servings
    )
    db.add(db_recipe)
    db.flush()  # .flush() permet de générer l'ID du nouvel objet Recipe avant de l'utiliser pour créer les relations avec les ingrédients. Cela garantit que l'ID est disponible pour les relations, même si la transaction n'est pas encore validée (commit).
    # Création des associations recette-ingrédient.
    # get_or_create_ingredient évite les doublons : si l'ingrédient existe déjà en base
    # (même nom normalisé en minuscules), il est réutilisé ; sinon il est créé.
    for ingredients_in in recipe_in.ingredients:
        db_ingredient = get_or_create_ingredient(db, ingredients_in.ingredient_name)
        db_recipe_ingredient = RecipeIngredient(
            recipe_id=db_recipe.id,
            ingredient_id=db_ingredient.id,
            quantity=ingredients_in.quantity,
            unit=ingredients_in.unit
        )
        db.add(db_recipe_ingredient)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def update_recipe(db: Session, recipe_id: int, recipe_in: RecipeUpdate) -> Recipe | None:
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None

    for field, value in recipe_in.model_dump(exclude_unset=True).items():   # .model_dump(exclude_unset=True) permet de ne récupérer que les champs qui ont été modifiés dans l'objet RecipeUpdate, en excluant ceux qui n'ont pas été définis (unset). Cela permet d'éviter de réécrire des valeurs par défaut ou nulles pour les champs non modifiés. 
        # Stratégie "replace" : on supprime tous les ingrédients existants de la recette
        # et on recrée ceux envoyés par le formulaire. Plus simple qu'un diff ligne par ligne.
        if field == "ingredients":
            # Supprimer les ingrédients existants
            db.query(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id).delete()
            # Ajouter les nouveaux ingrédients
            for ingredients_in in value:
                db_ingredient = get_or_create_ingredient(db, ingredients_in["ingredient_name"])
                db_recipe_ingredient = RecipeIngredient(
                    recipe_id=db_recipe.id,
                    ingredient_id=db_ingredient.id,
                    quantity=ingredients_in.get("quantity"),
                    unit=ingredients_in.get("unit")
                )
                db.add(db_recipe_ingredient)
        else:
            setattr(db_recipe, field, value)    # setattr(db_recipe, field, value) permet de mettre à jour dynamiquement les attributs de l'objet db_recipe avec les nouvelles valeurs fournies dans recipe_in. Cela évite d'avoir à écrire manuellement chaque champ à mettre à jour.

    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, recipe_id: int) -> Recipe | None:
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None

    db.delete(db_recipe)
    db.commit()
    return db_recipe

def get_or_create_ingredient(db: Session, ingredient_name: str) -> Ingredient:
    db_ingredient = db.query(Ingredient).filter(Ingredient.name == ingredient_name.strip().lower()).first()
    if db_ingredient is None:
        db_ingredient = Ingredient(name=ingredient_name.strip().lower())
        db.add(db_ingredient)
        db.flush()
    return db_ingredient

def get_ingredients(db: Session) -> list[Ingredient]:
    return db.query(Ingredient).order_by(Ingredient.name).all()