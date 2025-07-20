import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from playwright.async_api import async_playwright
import os

API_TOKEN = os.getenv('API_TOKEN')
if not API_TOKEN:
    raise ValueError("8139589288:AAE99b6afU4trVS9z5_n8wvBEZqVvA_sjTw")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def fetch_part_data(part_number: str) -> str:
    url = "https://parts.renault.ua/showbycode"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        await page.fill('input[name="code"]', part_number)
        await page.click('button[type="submit"]')
        try:
            await page.wait_for_selector(".search-result", timeout=10000)
            name = await page.inner_text('.search-result .result-title')
            availability = await page.inner_text('.search-result .result-available')
            price = await page.inner_text('.search-result .result-price')
        except:
            await browser.close()
            return f"❌ Деталь {part_number} не знайдено."
        await browser.close()
        return f"🔧 Номер: {part_number}\n📦 Назва: {name}\n✅ Наявність: {availability}\n💰 Ціна: {price}"

@dp.message_handler()
async def handle_message(message: Message):
    code = message.text.strip()
    if not code.isdigit():
        await message.reply("Введи тільки номер деталі (тільки цифри).")
        return
    await message.reply("🔎 Шукаю...")
    result = await fetch_part_data(code)
    await message.reply(result)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
