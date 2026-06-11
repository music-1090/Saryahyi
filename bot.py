import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fragment_api_lib.client import FragmentAPIClient

# ==================== တည်းဖြတ်ရန် နေရာများ ====================
BOT_TOKEN = "YOUR_BOT_TOKEN"          # သင့် Telegram Bot Token ထည့်ရန်
SUPPORT_USERNAME = "myanmar_music_bot2027"  # သင့် Support Account (ဥပမာ - thazin_tzk)
ADMIN_ID = 8315544720               # သင့်ရဲ့ Telegram User ID (ဒီထဲကို ငွေလွှဲအကြောင်းကြားစာလာမည်)

# ငွေလွှဲလက်ခံမည့် အချက်အလက်များ
PAYMENT_INFO = """
💵 **ငွေပေးချေရမည့် နည်းလမ်းများ**

ℹ️ **KBZPay**
နံပါတ် - `09444123849`
အမည် - Thaw Zin

ℹ️ **WavePay**
နံပါတ် - `09444123849`
အမည် - Thaw Zin

⚠️ ငွေလွှဲပြီးပါက Screenshot (ဘောင်ချာ) ကို ဒီ Bot ထဲသို့ ပို့ပေးရပါမည်။
"""

TON_SEED = "word1 word2 word3 ... word24"
FRAGMENT_COOKIES = "stel_ssid=...; stel_dt=...; stel_token=...; stel_ton_token=..."

# ပက်ကေ့စ်များနှင့် မြန်မာငွေဈေးနှုန်းများ (စိတ်ကြိုက် ပြင်နိုင်ပါသည်)
STAR_PACKAGES = {
    "50":   {"stars": 50,   "price": 3500},
    "75":   {"stars": 75,   "price": 5200},
    "100":  {"stars": 100,  "price": 6900},
    "250":  {"stars": 250,  "price": 17000},
    "500":  {"stars": 500,  "price": 35000},
    "1000": {"stars": 1000, "price": 70000},
}

PREMIUM_PACKAGES = {
    "3":  {"months": 3,  "price": 55000},
    "6":  {"months": 6,  "price": 75000},
    "12": {"months": 12, "price": 135000},
}
# ============================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
fragment = FragmentAPIClient()

class OrderState(StatesGroup):
    waiting_for_username = State()
    waiting_for_screenshot = State()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Telegram Stars ဝယ်ယူရန်", callback_data="buy_stars")],
        [InlineKeyboardButton(text="👑 Telegram Premium ဝယ်ယူရန်", callback_data="buy_premium")],
        [InlineKeyboardButton(text="💬 ကူညီဆောင်ရွက်ရေး (Support)", url=f"https://t.me/{SUPPORT_USERNAME}")],
    ])

def stars_menu():
    buttons = []
    for key, pkg in STAR_PACKAGES.items():
        buttons.append([InlineKeyboardButton(
            text=f"⭐ {pkg['stars']} Stars — {pkg['price']:,} MMK",
            callback_data=f"stars_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ ပင်မမီနူးသို့", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def premium_menu():
    buttons = []
    for key, pkg in PREMIUM_PACKAGES.items():
        buttons.append([InlineKeyboardButton(
            text=f"👑 {pkg['months']} လစာ — {pkg['price']:,} MMK",
            callback_data=f"premium_{key}"
        )])
    buttons.append([InlineKeyboardButton(text="◀️ ပင်မမီနူးသို့", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def recipient_menu(key, prefix="stars"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 မိမိကိုယ်တိုင်အတွက်", callback_data=f"self_{prefix}_{key}")],
        [InlineKeyboardButton(text="👥 သူငယ်ချင်းအတွက်", callback_data=f"friend_{prefix}_{key}")],
        [InlineKeyboardButton(
            text="◀️ နောက်သို့",
            callback_data="buy_stars" if prefix == "stars" else "buy_premium"
        )],
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 **TZK Digital Services Bot မှ ကြိုဆိုပါတယ်!**\n\n"
        "⭐ Telegram Stars နှင့် Premium များကို မြန်မာကျပ်ငွေဖြင့် လွယ်ကူလျင်မြန်စွာ ဝယ်ယူနိုင်ပါပြီ။\n\n"
        "လုပ်ဆောင်လိုသည့် ဝန်ဆောင်မှုကို ရွေးချယ်ပါ -",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "👋 **TZK Digital Services Bot မှ ကြိုဆိုပါတယ်!**\n\n"
        "⭐ Telegram Stars နှင့် Premium များကို မြန်မာကျပ်ငွေဖြင့် လွယ်ကူလျင်မြန်စွာ ဝယ်ယူနိုင်ပါပြီ။\n\n"
        "လုပ်ဆောင်လိုသည့် ဝန်ဆောင်မှုကို ရွေးချယ်ပါ -",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ===== STARS SECTION =====
@dp.callback_query(F.data == "buy_stars")
async def buy_stars(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ **ဝယ်ယူလိုသည့် Stars ပက်ကေ့စ်ကို ရွေးချယ်ပါ -**",
        reply_markup=stars_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("stars_"))
async def stars_selected(callback: CallbackQuery):
    key = callback.data.split("_")[1]
    pkg = STAR_PACKAGES[key]
    await callback.message.edit_text(
        f"⭐ **{pkg['stars']} Stars — {pkg['price']:,} MMK**\n\n"
        f"မည်သူ့ထံသို့ ပို့ဆောင်ရမလဲ ရွေးချယ်ပါ -",
        reply_markup=recipient_menu(key, "stars"),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("self_stars_"))
async def stars_for_self(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    username = callback.from_user.username
    if not username:
        await callback.answer("သင့်အကောင့်မှာ Username (ဥပမာ - @name) မရှိသေးပါသဖြင့် 'သူငယ်ချင်းအတွက်' မှတစ်ဆင့် ကိုယ်တိုင်ရိုက်ထည့်ပေးပါ!", show_alert=True)
        return
    await prompt_payment(callback.message, key, "stars", username, state)

@dp.callback_query(F.data.startswith("friend_stars_"))
async def stars_for_friend(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    await state.update_data(key=key, order_type="stars")
    await state.set_state(OrderState.waiting_for_username)
    await callback.message.edit_text(
        "👥 **လက်ခံမည့်သူ၏ Telegram Username ကို ရိုက်ထည့်ပါ -**\n\n"
        "ဥပမာ: `thawzin_tzk` သို့မဟုတ် `@thawzin_tzk`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ နောက်သို့", callback_data=f"stars_{key}")]
        ]),
        parse_mode="Markdown"
    )

# ===== PREMIUM SECTION =====
@dp.callback_query(F.data == "buy_premium")
async def buy_premium(callback: CallbackQuery):
    await callback.message.edit_text(
        "👑 **ဝယ်ယူလိုသည့် Premium သက်တမ်းကို ရွေးချယ်ပါ -**",
        reply_markup=premium_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("premium_"))
async def premium_selected(callback: CallbackQuery):
    key = callback.data.split("_")[1]
    pkg = PREMIUM_PACKAGES[key]
    await callback.message.edit_text(
        f"👑 **Telegram Premium {pkg['months']} လစာ — {pkg['price']:,} MMK**\n\n"
        f"မည်သူ့ထံသို့ ပို့ဆောင်ရမလဲ ရွေးချယ်ပါ -",
        reply_markup=recipient_menu(key, "premium"),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("self_premium_"))
async def premium_for_self(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    username = callback.from_user.username
    if not username:
        await callback.answer("သင့်အကောင့်မှာ Username မရှိပါသဖြင့် 'သူငယ်ချင်းအတွက်' မှတစ်ဆင့် ရိုက်ထည့်ပေးပါ!", show_alert=True)
        return
    await prompt_payment(callback.message, key, "premium", username, state)

@dp.callback_query(F.data.startswith("friend_premium_"))
async def premium_for_friend(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[2]
    await state.update_data(key=key, order_type="premium")
    await state.set_state(OrderState.waiting_for_username)
    await callback.message.edit_text(
        "👥 **လက်ခံမည့်သူ၏ Telegram Username ကို ရိုက်ထည့်ပါ -**\n\n"
        "ဥပမာ: `thawzin_tzk` သို့မဟုတ် `@thawzin_tzk`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ နောက်သို့", callback_data=f"premium_{key}")]
        ]),
        parse_mode="Markdown"
    )

# ===== USERNAME HANDLING =====
@dp.message(OrderState.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data["key"]
    order_type = data["order_type"]
    username = message.text.replace("@", "").strip()
    await prompt_payment(message, key, order_type, username, state)

# ===== PAYMENT PROMPT =====
async def prompt_payment(message_or_text, key, order_type, username, state: FSMContext):
    if order_type == "stars":
        pkg = STAR_PACKAGES[key]
        item_text = f"⭐ {pkg['stars']} Telegram Stars"
        price = pkg['price']
    else:
        pkg = PREMIUM_PACKAGES[key]
        item_text = f"👑 Telegram Premium ({pkg['months']} လစာ)"
        price = pkg['price']

    await state.update_data(item_text=item_text, price=price, username=username, key=key, order_type=order_type)
    await state.set_state(OrderState.waiting_for_screenshot)

    invoice_text = (
        f"📝 **အော်ဒါအသေးစိတ် အချက်အလက်**\n\n"
        f"📦 ပစ္စည်း: **{item_text}**\n"
        f"👤 လက်ခံမည့်သူ: **@{username}**\n"
        f"💵 ကျသင့်ငွေ: **{price} MMK**\n\n"
        f"{PAYMENT_INFO}\n"
        f"⬇️ ငွေလွှဲပြီးပါက အောက်တွင် ဘောင်ချာတင်ပေးပါရန်။"
    )

    if isinstance(message_or_text, Message):
        await message_or_text.answer(invoice_text, parse_mode="Markdown")
    else:
        await message_or_text.edit_text(invoice_text, parse_mode="Markdown")

# ===== SCREENSHOT VERIFICATION (ADMIN CONTROL) =====
@dp.message(OrderState.waiting_for_screenshot, F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    # လူကြီးမင်း (Admin) ဆီသို့ အော်ဒါသတင်းလှမ်းပို့ခြင်း
    admin_btn = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ အော်ဒါအတည်ပြုမည် (Auto Buy)", callback_data=f"approve_{data['order_type']}_{data['key']}_{data['username']}_{message.from_user.id}"),
            InlineKeyboardButton(text="❌ ငြင်းပယ်မည်", callback_data=f"reject_{message.from_user.id}")
        ]
    ])

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"🔔 **အော်ဒါအသစ် ရရှိပါသည်!**\n\n"
                f"👤 ဝယ်သူ ID: `{message.from_user.id}`\n"
                f"📦 အမယ်: {data['item_text']}\n"
                f"👥 ပို့ရမည့်သူ: @{data['username']}\n"
                f"💵 ပမာဏ: {data['price']:,} MMK\n\n"
                f"ဘောင်ချာ မှန်ကန်ပါက အောက်ပါခလုတ်ဖြင့် Fragment စနစ်ကို လုပ်ဆောင်ခိုင်းနိုင်ပါသည်၊၊",
        reply_markup=admin_btn,
        parse_mode="Markdown"
    )

    await message.answer("✅ **ဘောင်ချာ ပို့ဆောင်မှု အောင်မြင်ပါသည်။**\n\nလူကြီးမင်း၏ ငွေလွှဲမှုကို စစ်ဆေးပြီး မိနစ်ပိုင်းအတွင်း လုပ်ဆောင်ပေးသွားမည် ဖြစ်ပါသဖြင့် ခေတ္တစောင့်ဆိုင်းပေးပါဗျာ။")

@dp.message(OrderState.waiting_for_screenshot)
async def process_not_photo(message: Message):
    await message.answer("⚠️ ကျေးဇူးပြု၍ ငွေလွှဲဘောင်ချာ ဓာတ်ပုံ (Screenshot) ကို သာ ပို့ပေးပါရန်။")

# ===== ADMIN CALLBACK ACTIONS =====
@dp.callback_query(F.data.startswith("approve_"))
async def admin_approve(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_type, key, username, user_id = parts[1], parts[2], parts[3], parts[4]
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n⏳ **Fragment သို့ ချိတ်ဆက်နေပါသည်...**", parse_mode="Markdown")
    await bot.send_message(int(user_id), "⏳ Thaw Zin Services: **သင့်အော်ဒါကို ငွေလွှဲမှန်ကန်ကြောင်း အတည်ပြုပြီးပါပြီ။ Fragment မှတစ်ဆင့် ပစ္စည်းလွှဲပြောင်းပေးနေပါသည်။**")

    if order_type == "stars":
        pkg = STAR_PACKAGES[key]
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: fragment.buy_stars(
                username=username,
                amount=pkg["stars"],
                seed=TON_SEED,
                fragment_cookies=FRAGMENT_COOKIES
            )
        )
        if result:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ!**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"✅ **အောင်မြင်ပါသည်!**\n\n⭐ {pkg['stars']} Stars ကို @{username} ထံသို့ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ။ 🎉")
        else:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **Fragment Error ဖြစ်သွားပါသည်။**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"❌ စနစ်အတွင်း ချို့ယွင်းချက်ရှိ၍ ပစ္စည်းမရောက်ပါက support သို့ ဆက်သွယ်ပါ - @{SUPPORT_USERNAME}")

    elif order_type == "premium":
        pkg = PREMIUM_PACKAGES[key]
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: fragment.buy_premium(
                username=username,
                duration=pkg["months"],
                seed=TON_SEED,
                fragment_cookies=FRAGMENT_COOKIES
            )
        )
        if result:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ **Premium အောင်မြင်စွာ ပို့ပြီးပါပြီ!**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"✅ **အောင်မြင်ပါသည်!**\n\n👑 Telegram Premium {pkg['months']} လစာကို @{username} ထံသို့ အောင်မြင်စွာ Gift ပေးပြီးပါပြီ။ 🎉")
        else:
            await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **Fragment Error ဖြစ်သွားပါသည်။**", parse_mode="Markdown")
            await bot.send_message(int(user_id), f"❌ Premium တင်ရာတွင် ချို့ယွင်းချက်ရှိပါသဖြင့် support သို့ ဆက်သွယ်ပါ - @{SUPPORT_USERNAME}")

@dp.callback_query(F.data.startswith("reject_"))
async def admin_reject(callback: CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **ဒီအော်ဒါကို ငြင်းပယ်လိုက်သည်။**", parse_mode="Markdown")
    await bot.send_message(int(user_id), f"❌ **သင့်အော်ဒါ ငြင်းပယ်ခံရပါသည်။**\n\nငွေလွှဲမှု မှားယွင်းခြင်း သို့မဟုတ် ဘောင်ချာအဟောင်းဖြစ်နိုင်ပါသည်။ အသေးစိတ်ကို support သို့ မေးမြန်းနိုင်ပါသည် - @{SUPPORT_USERNAME}")

# ===== MAIN EXECUTION =====
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Manual Payment Verification Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
