from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import filters
from create import dp, bot
from config.config import *
from markups.usermarkups import create_markup, markup_start, create_inline_markup, navigator_callback
from state.userState import UserLogingState, update_state, UserReportState
from state.categories import categories_view
from create import database
from .Other_functions import check_name_right, check_phone_right


# command start
async def command_start(message: types.Message | types.CallbackQuery):
    # print(database.check_user(message.chat.id))
    if isinstance(message, types.Message):
        if database.check_user(message.chat.id) == "Ban":
            await message.answer("Вы забанены Администратором")
        if database.check_user(message.chat.id) == 1:
            await message.answer(text_in_start_old_user, reply_markup=markup_start)
        if database.check_user(message.chat.id) == 0:
            await message.answer(text_in_start_new_user)
            await UserLogingState.name.set()
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(text_in_start_old_user, reply_markup=markup_start)


async def name_validation(message: types.Message, state=FSMContext):
    name = await check_name_right(message)
    if isinstance(name, str):
        await state.update_data({"name":name})
        await message.answer(text_in_start_phone_number)
        await UserLogingState.next()


async def phone_validation(message: types.Message, state=FSMContext):
    phone = await check_phone_right(message)
    if isinstance(phone, str):
        await state.update_data({"phone": phone})
        data = await state.get_data()
        database.add_position(message.from_user.id, data["phone"], data["name"], "FALSE")
        await state.finish()
        await command_start(message)


# Get contact information about bot
async def contacts(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(contacts_in_start)


async def create_inline_menu(message: types.Message):
    await message.delete()
    first_dir = message.text
    path = []
    first_index, first_cats = categories_view(categories, path, first_dir=first_dir)
    markup = create_inline_markup(first_cats, first_index)
    await message.answer(categories_messages[str(first_index)], reply_markup=markup)



async def walk_in_dirs(callback: types.CallbackQuery, callback_data: dict):
    functions = {
        "00": create_report_start
    }
    await callback.message.delete()
    if not callback_data["Current_path"]:
        await command_start(callback)
    if callback_data["Current_path"] in ["00","01", "10", "11"]:
        await functions[str(callback_data["Current_path"])](callback, callback_data)

    else:
        cats = categories_view(categories, callback_data["Current_path"])
        markup = create_inline_markup(cats, callback_data["Current_path"])
        await callback.message.answer(categories_messages[callback_data["Current_path"]], reply_markup=markup)

async def create_report_start(callback: types.CallbackQuery, callback_data: dict):
    await UserReportState.address.set()
    cats = categories_view(categories, callback_data["Current_path"])
    markup = create_inline_markup(cats, callback_data["Current_path"])
    print(markup, type(markup))
    await callback.message.answer(categories_messages[callback_data["Current_path"]], reply_markup=markup)


async def report_callbacks(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    print(callback_data)

async def report_address(message: types.Message, state: FSMContext):
    await state.update_data({"address": message.text})
    cats = categories_view(categories, "000")
    markup = create_inline_markup(cats, "000")
    await message.answer(categories_messages["000"], reply_markup=markup)
    await UserReportState.next()

async def report_photo_check_type(message: types.Message, state: FSMContext):
    await message.answer(bad_message_in_report)

async def report_photo(message: types.Message, state: FSMContext):
    await state.update_data({"photo": message.photo[-1].file_id})
    cats = categories_view(categories, "0000")
    markup = create_inline_markup(cats, "0000")
    await message.answer(categories_messages["0000"], reply_markup=markup)
    await UserReportState.next()

async def report_reason(message: types.Message, state: FSMContext):
    await state.update_data({"message": message.text})
    all_data = await state.get_data()
    await state.finish()
    await message.answer("vse")



def register_user_handlers(dp:  Dispatcher):
    dp.register_message_handler(command_start, commands=["start"])

    dp.register_message_handler(name_validation, state=UserLogingState.name)
    dp.register_message_handler(phone_validation, state=UserLogingState.phone)
    dp.register_message_handler(contacts, lambda message: "Полезные контакты" in message.text)
    dp.register_message_handler(create_inline_menu, filters.Text(["⛔ Оставить заявку", "📞 Связаться", "⚙️ Настройки",
                                                                  "☎ Полезные контакты"]))
    dp.register_callback_query_handler(report_callbacks, navigator_callback.filter(), state=[UserReportState.address,UserReportState.reason,UserReportState.photo])
    dp.register_message_handler(report_address, state=UserReportState.address)
    dp.register_message_handler(report_photo_check_type, state=UserReportState.photo)
    dp.register_message_handler(report_photo, state=UserReportState.photo, content_types=["photo"])
    dp.register_message_handler(report_reason, state=UserReportState.reason)
    dp.register_callback_query_handler(walk_in_dirs, navigator_callback.filter())
