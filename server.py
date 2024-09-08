import flask
import sqlite3

from dataclasses import dataclass
from abc import ABC, abstractmethod

app     = flask.Flask(__name__)
db_name = 'data.db'

class Base(ABC):
    @abstractmethod
    def write_to_db(self, db_name):
        pass


@dataclass
class PreCommitUserData(Base):
    date            : str
    ip              : str
    behavior        : int
    actually_commit : str
    original_commit : str

    """ behavior
    0 : cancel  commit
    1 : no AI analyse,  use original commit
    2 : yes and use AI commit
    3 : yes and use original commit
    4 : yes but cancel the commit 
    """

    def write_to_db(self, db_name='data.db'):
        # Connect
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        # Create table
        c.execute('''CREATE TABLE IF NOT EXISTS PRE_COMMIT(
                id INTEGER PRIMARY KEY,
                date text,
                ip text,
                behavior int, 
                actually_commit text,
                original_commit text)''')

        c.execute("INSERT INTO PRE_COMMIT (date, ip, behavior, actually_commit, original_commit) VALUES (?, ?, ?, ?, ?)", 
                (self.date, self.ip, self.behavior, self.actually_commit, self.original_commit))
        
        conn.commit()
        conn.close()
        return self


@app.route('/pre_commit', methods=['POST'])
def pre_commit():
    data = flask.request.json
    data = PreCommitUserData(**data).write_to_db(db_name)
    print(data)
    return flask.jsonify(data)

if __name__ == '__main__':
    app.run(port=5010,host='0.0.0.0')