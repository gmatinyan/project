from jinja2 import StrictUndefined

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db
from flask import (Flask, render_template, redirect, request, flash,
                   session)


from model import User, Recipe, Favorite, Ingridient, RecipeIngridient, Tool, RecipeTool, Occasion, RecipeOccasion

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "goga"


# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
	"""Homepage."""

	recipes = Recipe.query.all()
	# make a second query for occasions
	
	return render_template("homepage.html", recipes=recipes)

@app.route('/search')
def search_cake():
	"""Searching cakes."""

	search = request.args.get('search')
	occasions = Occasion.query.filter(Occasion.oname.like('%' + search + '%')).all()
	recipe_names = Recipe.query.filter(Recipe.rname.like('%' + search + '%')).all()

	search_results = []

	for occasion in occasions:
		search_results.extend(occasion.recipes)

	search_results += recipe_names

	return render_template('search.html', search_results=search_results)


@app.route('/login', methods=['GET'])
def log_in_form():
	"""Logging users in by email & password"""

	return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_process():
	"""Process login."""

	email = request.form.get('email')
	password = request.form.get('password')

	user = User.query.filter_by(email=email).first()

	if user:
		if password == user.password:
			session['logged_in_user'] = user.user_id
			return redirect("/user_profile/{}".format(user.user_id))
		else:
			return redirect("/login")

	else:
		return redirect ("/register")



@app.route('/user_profile/<int:user_id>')
def user_info(user_id):
	"""Display user page."""

	user = User.query.get(user_id)
	recipes = Recipe.query.all()
	#recipes = set(recipes)

	return render_template("user_profile.html", user=user, recipes=recipes)




@app.route('/user_recipes')
def user_recipe():
	"""Showes all the recipes added by that user."""

	#query recipe tabel to get recipes by user.id
	user_id = session['logged_in_user']
	user_recipes = Recipe.query.filter_by(user_id=user_id).all()

	return render_template("user_recipes.html", user_recipes=user_recipes)


@app.route('/edit_recipe/<recipe_id>')
def show_user_recipe(recipe_id):
	"""Showes user the recipe that's added."""

	edit = Recipe.query.filter_by(recipe_id=recipe_id).first()
	edit_occasion = RecipeOccasion.query.filter_by(recipe_id=recipe_id).first()
	edit_ingridients = RecipeIngridient.query.filter_by(recipe_id=recipe_id).all()
	edit_tools = RecipeTool.query.filter_by(recipe_id=recipe_id).all()

	ingridient_names = {edit_ingridient.ingridient.iname for edit_ingridient in edit_ingridients}

	tool_names = {edit_tool.tool.tname for edit_tool in edit_tools}

	if edit_occasion:
		return render_template("edit_recipe.html", edit=edit, edit_occasion=edit_occasion.occasion, ingridient_names=ingridient_names, tool_names=tool_names, edit_ingridients=edit_ingridients, edit_tools=edit_tools)
	else:
		return render_template("edit_recipe.html", edit=edit, edit_occasion=" ", edit_ingridients=edit_ingridients, edit_tools=edit_tools)


@app.route('/edit_recipe/<recipe_id>', methods=['POST'])
def edit_user_recipe(recipe_id):
	"""Gives users ability to edit recipe."""

	user_id = session['logged_in_user']

	form_img_url = request.form.get('img_url')
	recipe_img = Recipe.query.filter_by(img_url='img_url').first()

	if form_img_url != recipe_img.img_url:
		recipe_img.img_url = form_img_url

	form_title = request.form.get('title')
	recipe_title = Recipe.query.filter_by(rname='title').first()

	if form_title != recipe_title.rname:
		recipe_title.rname = form_title

	form_occasion = request.form.get('occasion').lower()
	occasion = Occasion.query.filter_by(oname='occasion').first()

	if form_occasion != occasion.oname:
		occasion.oname = form_occasion

	form_description = request.form.get('description')
	recipe_description = Recipe.query.filter_by(style='description').first()

	if form_description != recipe_description.style:
		recipe_description.style = form_description

	
	form_ingridients = request.form.getlist('ingridients')

	ingridient_ids = []

	for ingridient in form_ingridients:
		ingridient_id = ingridient.query.filter_by(iname=ingridient).first()
		ingridient_ids.append(ingridient_id)
	
	recipeingridients = RecipeIngridient.query.filter_by(recipe_id=recipe_id).all()

	for recipeingredient_obj in recipeingredients:
		if  recipeingredient_obj.ingridient_id not in ingridient_ids:
			db.session.delete(recipeingredient_obj)

	for ingridient_id in ingridient_ids:
		if ingridient_id not in recipeingredients_obj:
			db.session.add(recipeingredient_obj)


	#form_ings = get all checked ingredients from the form
	#db_ings = get all recipieingredients.ingredients from the db
	#for db_ing in db_ings:
		#if ing.iname not in form_ings:
			#delete recipeingredient from db

	#for form_ing in form_ings:
		#if form_ing not in db_ings:
			#add new recipeingredient to db

	form_instructions = request.form.get('instructions')
	recipe_instructions = Recipe.query.filter_by(ingridients=instructions).first()

	if form_instructions != recipe_instructions.instructions:
		recipe_instructions.instructions = form_instructions


	db.session.commit()

	return redirect("/user_profile/{}".format(user_id))





@app.route('/logout')
def logout():
	"""Log out user."""

	session.clear()
	return redirect('/')



@app.route('/register', methods=['GET'])
def register_user():
	"""Register users."""

	return render_template("register.html")


@app.route('/register', methods=['POST'])
def verify_user():
	"""Check if user in db, if not add user to db."""

	first_name = request.form.get('fname')
	last_name = request.form.get('lname')
	email = request.form.get('email')
	password = request.form.get('password')

	user = User.query.filter_by(email=email).first()

	if not user:
		new_user = User(fname=first_name, lname=last_name, email=email, password=password)
		db.session.add(new_user)
		db.session.commit()
		session['logged_in_user'] = new_user.user_id
		return redirect("/user_profile/{}".format(new_user.user_id))
	else:
		return redirect('/login')



@app.route('/recipe/<recipe_id>')
def detaild_cake_view(recipe_id):
	"""cake detaild view."""

	recipe = Recipe.query.get(recipe_id)
	

	return render_template("cake_detail.html", recipe=recipe) 

@app.route('/add_new_recipe', methods=['GET'])
def show_new_recipe_form():
	"""Show add new recipe form"""


	return render_template("add_new_recipe.html")



@app.route('/add_new_recipe', methods=['POST'])
def add_new_recipe():
	"""Add new recipe to db."""


	user_id = session['logged_in_user']
	img_url = request.form.get('img_url')
	title = request.form.get('title')
	occasion = request.form.get('occasion').lower()

	occasion_check = Occasion.query.filter_by(oname=occasion).first()

	if not occasion_check:
		new_occasion = Occasion(oname = occasion)
		db.session.add(new_occasion)

	description = request.form.get('description')
	ingridients = request.form.getlist('ingridients')
	instructions = request.form.get('instructions')
	tools = request.form.getlist('tools')

	new_recipe = Recipe(img_url=img_url, rname=title, style=description, instructions=instructions, user_id=user_id)
	db.session.add(new_recipe)
	db.session.commit()

	if not occasion_check:
		new_recipe_occasion = RecipeOccasion(recipe_id=new_recipe.recipe_id, occasion_id=new_occasion.occasion_id)
	else:
		new_recipe_occasion = RecipeOccasion(recipe_id=new_recipe.recipe_id, occasion_id=occasion_check.occasion_id)

	db.session.add(new_recipe_occasion)

	for ingridient in ingridients:
		ingreident_obj = Ingridient.query.filter_by(iname=ingridient).first()
		recipe_ingrident = RecipeIngridient(ingridient_id=ingreident_obj.ingridient_id, recipe_id=new_recipe.recipe_id)
		db.session.add(recipe_ingrident)
	for tool in tools:
		tool_obj = Tool.query.filter_by(tname=tool).first()
		recipe_tool = RecipeTool(tool_id=tool_obj.tool_id, recipe_id=new_recipe.recipe_id)
		db.session.add(recipe_tool)

	db.session.commit()

	return redirect("/user_profile/{}".format(user_id))



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')


