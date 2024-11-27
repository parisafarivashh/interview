from zibal_project.utils import create_connection_db


class BaseMedium:
    def send(self, notification):
        raise NotImplementedError("Subclasses must implement this method.")


class SMSMedium(BaseMedium):
    def send(self, notification):
        self.get_template()
        print('send data based on template')

    @staticmethod
    def set_template(template_text: str, title: str):
        _create_message_template('sms', template_text, title)

    @staticmethod
    def get_template():
        return _get_message_template('email', 'title')


class EmailMedium(BaseMedium):
    def send(self, notification):
        self.get_template()
        print('send data based on template')

    @staticmethod
    def set_template(template_text: str, title: str):
        _create_message_template('email', template_text, title)

    @staticmethod
    def get_template():
        return _get_message_template('email', 'title')


def get_medium(medium_name: str):
    mediums = {
        'sms': SMSMedium(),
        'email': EmailMedium(),
    }
    return mediums.get(medium_name)


def _create_message_template(
        medium_type: str,
        template_text: str,
        title: str
):
    db = create_connection_db()
    template = {
        "medium_type": medium_type,
        "template": template_text,
        "title": title,
    }
    db.templetes.insert_one(template)

def _get_message_template(medium_type: str, title: str):
    db = create_connection_db()
    dict_ = db.templetes.find_one({'medium_type': medium_type, 'title': title})
    return dict_['template'] if dict_ else ''

