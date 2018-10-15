import graphene

from graphql import GraphQLError
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from ..models import Recipe, RecipeElement


# Types

class RecipeElementNode(DjangoObjectType):
    unit_display = graphene.String()

    class Meta:
        model = RecipeElement
        exclude_fields = ['recipe']
        interfaces = [relay.Node]

    def resolve_unit_display(self, info, **kwargs):
        return self.get_unit_display()

class RecipeNode(DjangoObjectType):

    class Meta:
        model = Recipe
        interfaces = [relay.Node]
        filter_fields = []

class RecipeQuery(object):
    recipe = relay.Node.Field(RecipeNode)
    all_recipes = DjangoFilterConnectionField(RecipeNode)


# Mutations

class RecipeElementInput(graphene.InputObjectType):
    ingredient = graphene.ID(required=True)
    amount = graphene.Float(required=True)
    unit = RecipeElementNode._meta.fields['unit']

class UpdateRecipeMutation(relay.ClientIDMutation):

    class Input:
        id = graphene.ID(required=True)
        title = graphene.String()
        instructions = graphene.String()
        featured = graphene.Boolean()
        elements = graphene.List(RecipeElementInput)

    recipe = graphene.Field(RecipeNode)

    @staticmethod
    def set_elements(info, recipe, elements):
        updates = []
        recipe.elements.all().delete()
        for element in elements:
            ingredient = relay.Node.get_node_from_global_id(info, element['ingredient'])
            updates.append(RecipeElement(
                recipe=recipe,
                ingredient=ingredient,
                amount=element['amount'],
                unit=element['unit']
            ))
        RecipeElement.objects.bulk_create(updates)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        id = input.pop('id')
        recipe = relay.Node.get_node_from_global_id(info, id)
        if recipe is None:
            raise GraphQLError('Recipe does not exist')

        elements = input.pop('elements', [])
        cls.set_elements(info, recipe, elements)

        for k, v in input.items():
            setattr(recipe, k, v)
        recipe.save()
        return cls(recipe=recipe)

class RecipeMutation(object):
    update_recipe = UpdateRecipeMutation.Field()
