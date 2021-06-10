import sys
import datetime

from flask import Flask, abort, request
from flask_restful import Resource, Api, inputs, reqparse, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()

resource_field = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.String
}


# write your code here
class QueryAll(Resource):
    @marshal_with(resource_field)
    def get(self):
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        if start_time and end_time:
            event = Events.query.filter(Events.date >= start_time, Events.date <= end_time).all()
            if event is None:
                abort(404, "The event doesn't exist!")
            return event
        else:
            return Events.query.all()


class QueryToday(Resource):
    @marshal_with(resource_field)
    def get(self):
        return Events.query.filter_by(date=datetime.date.today()).all()


class EventsPost(Resource):
    def post(self):
        parser.add_argument(
            'date',
            type=inputs.date,
            help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
            required=True
        )
        parser.add_argument(
            'event',
            type=str,
            help="The event name is required!",
            required=True
        )
        args = parser.parse_args()
        event = Events(event=args['event'], date=args['date'].date())
        db.session.add(event)
        db.session.commit()
        event = {'message': 'The event has been added!',
                 'event': args['event'],
                 'date': str(args['date'].date())}
        return event


class EventByID(Resource):
    @marshal_with(resource_field)
    def get(self, event_id):
        event = Events.query.filter(Events.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = Events.query.filter(Events.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
            event = {
                        "message": "The event has been deleted!"
                    }
        return event


api.add_resource(EventsPost, '/event')
api.add_resource(QueryAll, '/event')
api.add_resource(QueryToday, '/event/today')
api.add_resource(EventByID, '/event/<int:event_id>')


# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
