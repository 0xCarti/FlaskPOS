from sqlite3 import IntegrityError

from flask import Blueprint, render_template, url_for, redirect, flash, request, jsonify
from .forms import ItemForm, BulkDeleteForm, EventForm, ScreenForm
from .models import db, Item, Event, Transaction, Screen, ScreenItem

item = Blueprint('item', __name__)
event = Blueprint('event', __name__)
transaction = Blueprint('transaction', __name__)
screen = Blueprint('screen', __name__)


@item.route('/items/add_item', methods=['GET', 'POST'])
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(name=form.name.data, price=form.price.data, gl_code=form.gl_code.data)
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('item.view_items'))
    return render_template('items/add_item.html', form=form)


@item.route('/items')
def view_items():
    items = Item.query.all()
    form = BulkDeleteForm()
    return render_template('items/view_items.html', items=items, form=form)


@item.route('/items/bulk_delete', methods=['POST'])
def bulk_delete():
    selected_items = request.form.getlist('selected_items')
    if selected_items:
        Item.query.filter(Item.id.in_(selected_items)).delete(synchronize_session='fetch')
        db.session.commit()
    return redirect(url_for('item.view_items'))


@item.route('/items/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.gl_code = form.gl_code.data
        db.session.commit()
        flash('Item updated successfully.', 'success')
        return redirect(url_for('item.view_items'))
    return render_template('items/edit_item.html', form=form)


@event.route('/events')
def view_events():
    filter = request.args.get('filter', 'open')

    if filter == 'open':
        events = Event.query.filter_by(closed=False).all()
    elif filter == 'closed':
        events = Event.query.filter_by(closed=True).all()
    else:  # 'all' or any other value
        events = Event.query.all()

    form = BulkDeleteForm()
    return render_template('events/view_events.html', events=events, form=form, filter=filter)


@event.route('/events/add_event', methods=['GET', 'POST'])
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(name=form.name.data)
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!', 'success')
        return redirect(url_for('event.view_events'))
    return render_template('events/add_edit_event.html', form=form, title='Add Event')


@event.route('/events/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    if form.validate_on_submit():
        event.name = form.name.data
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('event.view_events'))
    return render_template('events/add_edit_event.html', form=form, title='Edit Event', event_id=event_id)


@event.route('/events/bulk_delete', methods=['POST'])
def bulk_delete_events():
    selected_events = request.form.getlist('selected_events')
    if selected_events:
        Event.query.filter(Event.id.in_(selected_events)).delete(synchronize_session='fetch')
        db.session.commit()
    return redirect(url_for('event.view_events'))


@event.route('/events/toggle_event_status/<int:event_id>', methods=['GET'])
def toggle_event_status(event_id):
    event = Event.query.get_or_404(event_id)
    event.closed = not event.closed
    db.session.commit()
    flash(f"Event {'closed' if event.closed else 'opened'} successfully.")
    return redirect(url_for('event.view_events'))


@event.route('/events/view_event/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    transactions = Transaction.query.filter_by(event_id=event_id).all()
    return render_template('events/view_event.html', event=event, transactions=transactions)


@transaction.route('/transactions/view_transaction/<int:transaction_id>')
def view_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    # Assume there are additional details to pass to the template
    return render_template('view_transaction.html', transaction=transaction)


@screen.route('/screens')
def view_screens():
    screens = Screen.query.all()
    form = BulkDeleteForm()
    return render_template('screens/view_screens.html', screens=screens, form=form)


@screen.route('/screens/view_screen/<int:screen_id>')
def view_screen(screen_id):
    screen = Screen.query.get_or_404(screen_id)
    # Assuming ScreenItem has 'item' relationship and 'priority' for ordering
    screen_items = sorted(screen.items, key=lambda si: si.priority)
    return render_template('screens/view_screen.html', screen=screen, screen_items=screen_items)


# Helper function to parse items from form data
def parse_items(form_data):
    items = []
    for key, value in form_data.items():
        if key.startswith('items[') and key.endswith('][id]'):
            _, index, _ = key.strip(']').split('[')
            item_id = value
            priority_key = f'items[{index}[priority]'
            priority = form_data.get(priority_key, '0')
            items.append({'id': int(item_id), 'priority': int(priority)})
    return items


@screen.route('/screens/add_screen', methods=['GET', 'POST'])
def add_screen():
    form = ScreenForm()
    if form.validate_on_submit():
        existing_screen = Screen.query.filter_by(name=form.name.data).first()
        if existing_screen is None:
            new_screen = Screen(
                name=form.name.data,
                event_id=form.event_id.data
            )
            db.session.add(new_screen)
            db.session.flush()  # Ensure new_screen has an ID for association

            # Parse items from form data
            items = parse_items(request.form)

            print(items)

            # Create ScreenItem associations
            for item_data in items:
                new_association = ScreenItem(
                    screen_id=new_screen.id,
                    item_id=item_data['id'],
                    priority=item_data['priority']
                )
                db.session.add(new_association)

            try:
                db.session.commit()
                flash('Screen added successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while adding the screen.', 'danger')
            return redirect(url_for('screen.view_screens'))
        else:
            flash('A screen with this name already exists.', 'danger')
    return render_template('screens/add_edit_screen.html', form=form)


@screen.route('/screen/edit_screen/<int:screen_id>', methods=['GET', 'POST'])
def edit_screen(screen_id):
    screen = Screen.query.get_or_404(screen_id)
    form = ScreenForm(obj=screen)

    existing_items = []
    if request.method == 'GET':
        form.event_id.data = screen.event_id
        # Fetch existing items and their priorities for the screen
        existing_items = [
            {
                'item_id': screen_item.item_id,
                'item_name': screen_item.item.name,  # Assuming the Item model has a 'name' attribute
                'priority': screen_item.priority
            }
            for screen_item in screen.items
        ]

    if form.validate_on_submit():
        existing_screen = Screen.query.filter(Screen.id != screen_id, Screen.name == form.name.data).first()
        if existing_screen is None:
            screen.name = form.name.data
            screen.event_id = form.event_id.data

            # Clear existing ScreenItem associations
            ScreenItem.query.filter_by(screen_id=screen.id).delete()

            # Parse new items from form data
            items = parse_items(request.form)
            print(items)
            for item_data in items:
                new_association = ScreenItem(
                    screen_id=screen.id,
                    item_id=item_data['id'],
                    priority=item_data['priority']
                )
                db.session.add(new_association)

            try:
                db.session.commit()
                flash('Screen updated successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while updating the screen.', 'danger')
            return redirect(url_for('screen.view_screens'))
        else:
            flash('A screen with this name already exists.', 'danger')

    return render_template('screens/add_edit_screen.html', form=form, screen_id=screen_id, existing_items=existing_items)


@screen.route('/screens/bulk_delete', methods=['POST'])
def bulk_delete_screens():
    selected_screens = request.form.getlist('selected_screens')
    if selected_screens:
        Screen.query.filter(Screen.id.in_(selected_screens)).delete(synchronize_session='fetch')
        db.session.commit()
    return redirect(url_for('screen.view_screens'))


@item.route('/items/item_suggestions')
def item_suggestions():
    query = request.args.get('query', '')
    items = Item.query.filter(Item.name.ilike(f'%{query}%')).all() if query else []
    return jsonify([{'id': item.id, 'name': item.name} for item in items])
