from __main__ import db


class device(db.model):

    id = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self) -> None:
        super().__init__()
        self.isAlive = False
