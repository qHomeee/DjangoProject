const { chromium } = require("playwright");

const url = process.argv[2] || "http://127.0.0.1:8000/";
const output = process.argv[3] || "screenshot.png";
const chromePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

(async () => {
    const browser = await chromium.launch({ headless: true, executablePath: chromePath });
    const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForSelector(".sneaker-viewer canvas", { timeout: 15000 });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: output, fullPage: false });
    await browser.close();
    console.log(output);
})();
