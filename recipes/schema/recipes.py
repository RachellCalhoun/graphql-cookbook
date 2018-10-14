import graphene
from graphene_django.types import DjangoObjectType

from ..models import Recipe, RecipeElement


class RecipeElementNode(DjangoObjectType):

    class Meta:
        model = RecipeElement

class RecipeNode(DjangoObjectType):

    class Meta:
        model = Recipe

class RecipeQuery(object):
    recipe = graphene.Field(RecipeNode, id=graphene.Int(required=True))
    all_recipes = graphene.List(RecipeNode)

    def resolve_recipe(self, info, **kwargs):
        id = kwargs.get('id')
        try:
            return Recipe.objects.get(pk=id)
        except (Recipe.DoesNotExist):
            return None

    def resolve_all_recipes(self, info, **kwargs):
        return Recipe.objects.all()
