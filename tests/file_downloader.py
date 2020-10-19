import flask

web = flask.Flask(__name__)


@web.route('/load')
def load_agent():
    return flask.send_file('/root/oiagentsv2.tar')


if __name__ == '__main__':
    web.run(
        host='0.0.0.0',
        port=8001
    )
