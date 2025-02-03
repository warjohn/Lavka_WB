from aiogram.fsm.state import State, StatesGroup

class ALL_STATE(StatesGroup):
    market = State()
    main = State()
    admin = State()
    all_rules = State()
    first_good = State()
    anketa = State()
    set_image = State()
    upload_images = State()
    chose_goods = State()
    kat = State()
    admin_user = State()


class Anketa_state_key(StatesGroup):
    one = State()
    two = State()
    betwen = State()
    three = State()
    four = State()
    five = State()
    six = State()
    seven = State()
    eight = State()
    nine = State()
    ten = State()
    eleven = State()

class Anketa_state_other(StatesGroup):
    one = State()
    two = State()
    betwen = State()
    three = State()
    four = State()
    five = State()
    six = State()
    seven = State()
    eight = State()