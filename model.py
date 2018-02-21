
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
	"""User of cake decorating website."""

	__tablename__ = "users"

	user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	fname = db.Column(db.String(25), nullable=False)
	lname = db.Column(db.String(25), nullable=False)
	email = db.Column(db.String(64), nullable=False)
	password = db.Column(db.String(64), nullable=False)

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<User user_id={}, fname={}, lname={}>".format(self.user_id, 
															  self.fname, 
															  self.lname)


class Recipe(db.Model):
	"""Recipe information."""

	__tablename__ = "recipes"

	recipe_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	rname = db.Column(db.String(100), nullable=False)
	instructions = db.Column(db.String(500), nullable=False)
	style = db.Column(db.String(100), nullable=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
	img_url = db.Column(db.String(700), nullable=False)

	# Define relationship to users
	user = db.relationship("User", backref="recipes")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<Recipe recipe_id={}, rname={}, user_id={},>".format(self.recipe_id, 
														 			 self.rname, 
														 			 self.user_id)


class Rating(db.Model):
	"""Rating information."""

	__tablename__ = "ratings"

	rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
	score = db.Column(db.Integer, nullable=False)

	user_rating = db.relationship("User", backref="ratings")

	recipe_rating = db.relationship("Recipe", backref="ratings")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<rating_id={} score={}>".format(self.rating_id, self.score)



class Favorite(db.Model):
	"""Favorite information."""

	__tablename__ = "favorites"

	favorite_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)

	# Define relationship to user
	user_favorite = db.relationship("User", backref="favorites")

	# Define relationship to recipe
	recipe_favorite = db.relationship("Recipe", backref="favorites")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<Favorite favorite_id={}, user_id={}, recipe_id={}>".format(self.favorite_id,
																			self.user_id,
																			self.recipe_id)

class Ingridient(db.Model):
	"""Ingridient information."""

	__tablename__ = "ingridients"

	ingridient_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	iname = db.Column(db.String(50), nullable=False)

	tool_ingridients = db.relationship("Recipe", secondary="recipe_ingridients", backref="ingridients")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<Ingridient ingridient_id={}, iname={}>".format(self.ingridient_id, self.iname)


class RecipeIngridient(db.Model):
	"""Aassociation table between recipes and ingridients."""

	__tablename__ = "recipe_ingridients"

	ri_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
	ingridient_id = db.Column(db.Integer, db.ForeignKey('ingridients.ingridient_id'), nullable=False)

	# Define relationship to recipe
	recipe_ingridient = db.relationship("Recipe", backref="recipe_ingridients")

	# Define relationship to ingridients
	ingridient = db.relationship("Ingridient", backref="recipe_ingridients")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<RecipeIngridient ri_id={}, recipe_id={}, ingridient_id={}>".format(self.ri_id, 
																					self.recipe_id, 
																					self.ingridient_id)


class RecipeTool(db.Model):
	"""Aassociation table between recipes and tools."""

	__tablename__ = "recipe_tools"

	rt_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
	tool_id = db.Column(db.Integer, db.ForeignKey('tools.tool_id'), nullable=False)

	recipe_tool = db.relationship("Recipe", backref="recipe_tools")

	tool = db.relationship("Tool", backref="recipe_tools")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<RecipeTool rt_id={}, recipe_id={}, tool_id={}>".format(self.rt_id,
																	    self.recipe_id,
																	    self.tool_id)



class Tool(db.Model):
	"""Information about tools."""

	__tablename__ = "tools"

	tool_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	tname = db.Column(db.String(50), nullable=False)

	tool_recipes = db.relationship("Recipe", secondary="recipe_tools", backref="tools")

	
	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<Tool tool_id={}, tname={}>".format(self.tool_id, self.tname)




class Occasion(db.Model):
	"""Occasion information."""
	
	__tablename__ = "occasions"


	occasion_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	oname = db.Column(db.String(50), nullable=False)

	recipes = db.relationship("Recipe",  secondary="recipe_occasions", backref="occasions")

	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<Occasion occasion_id={}, oname={}>".format(self.occasion_id,
															self.oname)


class RecipeOccasion(db.Model):
	"""Aassociation table between recipes and occasions."""

	__tablename__ = "recipe_occasions"
	

	ro_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), nullable=False)
	occasion_id = db.Column(db.Integer, db.ForeignKey('occasions.occasion_id'), nullable=False)

	recipe_occasion = db.relationship("Recipe", backref="recipe_occasions")

	occasion = db.relationship("Occasion", backref="recipe_occasions")


	def __repr__(self):
		"""Provide helpful representation when printed."""

		return "<RecipeOccasion ro_id={}, recipe_id={}, occasion_id={}>".format(self.ro_id,
																				self.recipe_id,
																				self.occasion_id)


def example_data():
	"""Add data to database.""" 

	User.query.delete()
	Recipe.query.delete()
	Favorite.query.delete()
	Ingridient.query.delete()
	RecipeIngridient.query.delete()
	RecipeTool.query.delete()
	Tool.query.delete()
	Occasion.query.delete()
	RecipeOccasion.query.delete()

	gohar = User(fname='Gohar', lname='Matinyan', email='gm@gmail.com', password='123')
	andrey = User(fname='Andrey', lname='Khalpakhchyan', email='ak@gmail.com', password='abc')
	lilit = User(fname='Lilit', lname='Buniatyan', email='lb@yahoo.com', password='def')

	buttercream = Ingridient(iname='buttercream') 
	whipped_cream = Ingridient(iname='whipped_cream')
	ganache = Ingridient(iname='ganache')
	royal_icing = Ingridient(iname='royal_icing')
	fondant = Ingridient(iname='fondant')

	cake_turntable = Tool(tname="cake_turntable")
	decorating_kit = Tool(tname="decorating_kit")
	icing_comb = Tool(tname='icing_comb')
	
	wedding = Occasion(oname='wedding')
	birthday = Occasion(oname='birthday')
	graduation = Occasion(oname='graduation')
	baptism = Occasion(oname='baptism')

	rwedding = Recipe(rname='wedding', instructions='wedding cake decorating instruction', style='elegant', img_url='https://static.wixstatic.com/media/692f6e_24fa7935040941cfbe3b22cbc81d856a.jpg/v1/crop/x_225,y_211,w_2388,h_4037/fill/w_324,h_581,al_c,q_80,usm_0.66_1.00_0.01/692f6e_24fa7935040941cfbe3b22cbc81d856a.webp')
	rbirthday = Recipe(rname='birthday', instructions='birthday cake decorating instructions', style='girl', img_url='https://namebirthdaycakes.com/images/styles/best-strawberry-cake-for-happy-birthday-with-name-f142.png')
	rgraduation = Recipe(rname='graduation', instructions='graduation cake decorating instructions', style='boy', img_url='https://i.pinimg.com/736x/cd/ba/75/cdba7509591a48555aed24ad896926de--graduation-celebration-graduation-ideas.jpg')
	rbaptism = Recipe(rname='baptism', instructions='baptism cake decorating instructions', style='unisex', img_url='https://www.myhappybirthdaywishes.com/wp-content/uploads/2016/09/angel-baptism-cakes-for-girls.jpg')

	rt1 = RecipeTool(recipe_tool=rwedding, tool=icing_comb)
	rt2 = RecipeTool(recipe_tool=rbirthday, tool=icing_comb)
	rt3 = RecipeTool(recipe_tool=rgraduation, tool=decorating_kit)
	rt4 = RecipeTool(recipe_tool=rbaptism, tool=decorating_kit)

	ri1 = RecipeIngridient(recipe_ingridient=rwedding, ingridient=buttercream)
	ri2 = RecipeIngridient(recipe_ingridient=rbirthday, ingridient=fondant)
	ri3 = RecipeIngridient(recipe_ingridient=rgraduation, ingridient=whipped_cream)
	ri4 = RecipeIngridient(recipe_ingridient=rbaptism, ingridient=fondant)

	ro1 = RecipeOccasion(recipe_occasion=rwedding, occasion=wedding)
	ro2 = RecipeOccasion(recipe_occasion=rbirthday, occasion=birthday)
	ro3 = RecipeOccasion(recipe_occasion=rgraduation, occasion=graduation)
	ro4 = RecipeOccasion(recipe_occasion=rbaptism, occasion=baptism)

	

	
	
	db.session.add_all([gohar, andrey, lilit])
	db.session.commit()
	

	db.session.add_all([rwedding, rbirthday, rgraduation, rbaptism])
	db.session.commit()
		


	db.session.add_all([buttercream, whipped_cream, ganache, royal_icing, fondant, 
						cake_turntable, decorating_kit, icing_comb, wedding, 
						birthday, graduation, baptism, rt1, rt2, 
						rt3, rt4, ri1, ri2, ri3, ri4, ro1, ro2, ro3, ro4])

	
	db.session.commit()




#######################################################################################################



def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipe-db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
    connect_to_db(app)
    db.create_all()
    example_data()


