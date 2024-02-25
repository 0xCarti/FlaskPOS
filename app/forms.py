from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired

from app.models import Event


class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    gl_code = StringField('GL Code', validators=[DataRequired()])
    submit = SubmitField('Create Item')


class BulkDeleteForm(FlaskForm):
    submit = SubmitField('Delete Selected')


class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    submit = SubmitField('Create Event')


class ScreenForm(FlaskForm):
    name = StringField('Screen Name', validators=[DataRequired()])
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ScreenForm, self).__init__(*args, **kwargs)
        # Dynamically set choices for event_id
        self.event_id.choices = [(e.id, e.name) for e in Event.query.order_by(Event.name).all()]
