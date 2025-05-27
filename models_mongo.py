from mongoengine import Document, StringField, FloatField

class Destination(Document):
    meta = {'collection': 'destinations'} 
    Destination = StringField(required=True)
    State = StringField(required=True)
    PopularSpot = StringField()
    Activities = StringField()
    Category = StringField()
    Price = FloatField()
    image_url = StringField()
    Title = StringField()
    Description = StringField()
 

