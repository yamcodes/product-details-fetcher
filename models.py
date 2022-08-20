from tortoise import Model, fields


class Details(Model):
    source_id = fields.CharField(50, pk=True)
    source = fields.CharField(7)
    title = fields.TextField()
    price = fields.FloatField()
    
class Favorites(Model):
    email = fields.CharField(50)
    product: fields.ForeignKeyRelation[Details] = fields.ForeignKeyField("models.Details", related_name="favorites", to_field="source_id")