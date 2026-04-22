const { chromium } = require("playwright");

const url = process.argv[2] || "http://127.0.0.1:8000/";
const chromePath = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

(async () => {
    const browser = await chromium.launch({ headless: true, executablePath: chromePath });
    const page = await browser.newPage({ viewport: { width: 1365, height: 900 } });
    const browserErrors = [];

    page.on("pageerror", (error) => browserErrors.push(error.message));
    page.on("console", (message) => {
        if (message.type() === "error") {
            browserErrors.push(message.text());
        }
    });

    await page.goto(url, { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".sneaker-viewer canvas", { timeout: 15000 });
    await page.waitForFunction(() => {
        const canvas = document.querySelector(".sneaker-viewer canvas");
        return canvas && canvas.width > 200 && canvas.height > 200;
    });
    await page.waitForTimeout(2500);

    const metrics = await page.evaluate(() => {
        const canvas = document.querySelector(".sneaker-viewer canvas");
        const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
        const image = canvas.toDataURL("image/png");

        return {
            canvasWidth: canvas.width,
            canvasHeight: canvas.height,
            imageLength: image.length,
            hasWebGl: Boolean(gl),
        };
    });

    await browser.close();

    if (browserErrors.length) {
        throw new Error(`Browser errors: ${browserErrors.join(" | ")}`);
    }

    if (!metrics.hasWebGl || metrics.imageLength < 10000) {
        throw new Error(`Canvas did not render expected 3D pixels: ${JSON.stringify(metrics)}`);
    }

    console.log(JSON.stringify(metrics));
})();
