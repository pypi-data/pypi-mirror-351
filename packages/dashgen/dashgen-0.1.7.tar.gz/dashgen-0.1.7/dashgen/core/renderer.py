import asyncio
from playwright.async_api import async_playwright

async def render_html_to_image(html, output_path, width, height):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html, wait_until="networkidle")

        # Esperar todos os gráficos renderizarem (canvas com altura visível)
        # Espera até que o scrollHeight pare de mudar
        await page.evaluate("""
          () => {
            return new Promise((resolve) => {
              let last = 0;
              let count = 0;

              const interval = setInterval(() => {
                const current = document.body.scrollHeight;
                if (current === last) {
                  count++;
                  if (count >= 3) {
                    clearInterval(interval);
                    resolve();
                  }
                } else {
                  count = 0;
                  last = current;
                }
              }, 100);
            });
          }
        """)


        await page.screenshot(path=output_path, full_page=False)
        await browser.close()
