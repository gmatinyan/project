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
			flash("Logged in")
			return redirect("/user_profile/{}".format(user.user_id))
		else:
			flash("Login failed")
			return redirect("/login")

	else:
		flash("You are not yet registered")
		return redirect ("/register")



@app.route('/user_profile/<int:user_id>')
def user_info(user_id):
	"""Display user page."""

	if 'logged_in_user' in session:
		user = User.query.get(user_id)
		recipes = Recipe.query.all()
	
		return render_template("user_profile.html", user=user, recipes=recipes)
	else:
		return redirect('/')



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

	
	return render_template("edit_recipe.html", edit=edit, edit_occasion=edit_occasion.occasion, 
												   recipe_id=recipe_id, ingridient_names=ingridient_names, 
												   tool_names=tool_names, edit_ingridients=edit_ingridients, 
												   edit_tools=edit_tools)
	

@app.route('/edit_recipe/<recipe_id>', methods=['POST'])
def edit_user_recipe(recipe_id):
	"""Gives users ability to edit recipe."""

	user_id = session['logged_in_user']

	form_img_url = request.form.get('img_url')
	recipe = Recipe.query.get(recipe_id)

	if form_img_url != recipe.img_url:
		recipe.img_url = form_img_url

	form_title = request.form.get('title')

	if form_title != recipe.rname:
		recipe.rname = form_title

	form_occasion = request.form.get('occasion').lower()
	occasion = recipe.occasions[0]

	if form_occasion != occasion.oname:
		occasion.oname = form_occasion

	form_description = request.form.get('description')
	
	if form_description != recipe.style:
		recipe.style = form_description

	
	form_ingridients = request.form.getlist('ingridients')

	ingridient_ids = []

	for ingridient in form_ingridients:
		ingridient_id = Ingridient.query.filter_by(iname=ingridient).first().ingridient_id
		ingridient_ids.append(ingridient_id)
	
	recipeingridients = RecipeIngridient.query.filter_by(recipe_id=recipe_id).all()


	for recipeingredient_obj in recipeingridients:
		if  recipeingredient_obj.ingridient_id not in ingridient_ids:
			db.session.delete(recipeingredient_obj)

	recipeingridient_ids = []

	for recipeingridient in recipeingridients:
		recipeingridient_id = recipeingridient.ingridient_id
		recipeingridient_ids.append(recipeingridient_id)

	for ingridient_id in ingridient_ids:
		if ingridient_id not in recipeingridient_ids:
			new_recipe_ingridient = RecipeIngridient(recipe_id=recipe_id, ingridient_id=ingridient_id)
			db.session.add(new_recipe_ingridient)


	form_instructions = request.form.get('instructions')
	

	if form_instructions != recipe.instructions:
		recipe.instructions = form_instructions


	form_tools = request.form.getlist('tools')

	tool_ids = []

	for tool in form_tools:
		tool_id = Tool.query.filter_by(tname=tool).first().tool_id
		tool_ids.append(tool_id)

	recipetools = RecipeTool.query.filter_by(recipe_id=recipe_id).all()

	for recipetool_obj in recipetools:
		if recipetool_obj.tool_id not in tool_ids:
			db.session.delete(recipetool_obj)

	recipetool_ids = []

	for recipetool in recipetools:
		recipetool_id = recipetool.tool_id
		recipetool_ids.append(recipetool_id)

	for tool_id in tool_ids:
		if tool_id not in recipetool_ids:
			new_recipe_tool = RecipeTool(recipe_id=recipe_id, tool_id=tool_id)
			db.session.add(new_recipe_tool)



	db.session.commit()

	return redirect("/user_profile/{}".format(user_id))





@app.route('/logout')
def logout():
	"""Log out user."""

	session.clear()
	flash("Logged out.")
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
		flash("Registerd.")
		return redirect("/user_profile/{}".format(new_user.user_id))
	else:
		flash("Please log in, you've already had account.")
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


