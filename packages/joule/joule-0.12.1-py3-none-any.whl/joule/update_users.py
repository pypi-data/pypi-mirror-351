from joule.models.master import Master
import logging
log = logging.getLogger('joule')

def update_users_from_file(users_file, db):
    log.info(f"Updating users based on [{users_file}]")
    with open(users_file, 'r') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0 or line.startswith('#'):
                continue  # ignore comments and blank lines

            if line.startswith('DELETE'):
                parse_removal(line, db)
            else:
                parse_addition(line, db)


def parse_removal(line, db):
    params = line.split(' ')
    if len(params) == 2:
        if params[0] != 'DELETE':
            log.error(f"ERROR: invalid delete syntax in users file: {line}")
            return
        remove_user(params[1], db)
    elif len(params) == 3:
        if params[0] != 'DELETE' or params[1] != 'LIKE':
            log.error(f"ERROR: invalid delete syntax in users file: {line}")
            return
        remove_user_like(params[2], db)
    else:
        log.error(f"ERROR: invalid delete syntax in users file: {line}")


def parse_addition(line, db):
    params = line.split(',')
    if len(params) != 2:
        log.error(f"ERROR: invalid syntax in users file: {line}")
        return
    user, key = params
    if len(key) < 10:
        log.error(f"ERROR: key is too short, must be >= 10 characters: {line}")
        return
    add_user(user.strip(), key.strip(), db)


def remove_user(user, db):
    users = db.query(Master). \
        filter(Master.name == user)
    for user in users:
        log.info(f"Removing user {user.name}")
        db.delete(user)
    db.commit()


def remove_user_like(name, db):
    users = db.query(Master). \
        filter(Master.name.like(name))
    for user in users:
        log.info(f"Removing user {user.name}")
        db.delete(user)
    db.commit()


def add_user(name, key, db):
    # if this key is for the same name, then nothing to do
    if db.query(Master).filter(Master.name == name).filter(Master.key == key).first():
        log.info(f"{name} already exists with this key")
        return
    # make sure the key does not exist already
    if db.query(Master).filter(Master.key==key).first():
        log.error(f"Cannot add {name}, the requested key is already associated with another user")
        return
    # check if this name already exists
    master = db.query(Master). \
        filter(Master.type == Master.TYPE.USER). \
        filter(Master.name == name).first()
    if master is not None:
        master.key = key
        log.info(f"Modifying API key for {name}")
    else:
        # create a new name
        master = Master(name=name,
                        type=Master.TYPE.USER,
                        key=key)
        master.grantor_id = None  # not granted by another name
        log.info(f"Adding user {name}")
    # save the changes
    db.add(master)
    db.commit()
