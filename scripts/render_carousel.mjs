#!/usr/bin/env node

import { realpathSync } from "node:fs";
import { isAbsolute, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

function parseArgs(values) {
  const args = {};
  for (let index = 0; index < values.length; index += 2) {
    const key = values[index];
    const value = values[index + 1];
    if (!key?.startsWith("--") || value === undefined) {
      throw new Error("renderer arguments must be --key value pairs");
    }
    args[key.slice(2)] = value;
  }
  return args;
}

function isInside(path, root) {
  const child = relative(root, path);
  return child === "" || (!child.startsWith(`..${sep}`) && child !== ".." && !isAbsolute(child));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const required = ["url", "project", "output", "har", "width", "height", "slide", "wait-ms"];
  for (const name of required) {
    if (!args[name]) throw new Error(`missing --${name}`);
  }

  const project = realpathSync(args.project);
  const blocked = [];
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: Number(args.width), height: Number(args.height) },
    recordHar: { path: args.har, mode: "full", content: "embed" },
    javaScriptEnabled: false,
    serviceWorkers: "block",
  });

  try {
    // Both routes exist before any Page is created, so non-local network and
    // out-of-project file traffic cannot leave the browser context first.
    await context.route("**/*", async (route) => {
      const requestUrl = route.request().url();
      const parsed = new URL(requestUrl);
      if (["data:", "blob:", "about:"].includes(parsed.protocol)) {
        await route.continue();
        return;
      }
      if (parsed.protocol === "file:") {
        try {
          const local = realpathSync(fileURLToPath(parsed));
          if (isInside(local, project)) {
            await route.continue();
            return;
          }
        } catch {
          // Missing or unresolvable local files are blocked and reported below.
        }
      }
      blocked.push({ kind: "request", method: route.request().method(), url: requestUrl });
      await route.abort("blockedbyclient");
    });

    // context.route() does not intercept WebSocket handshakes. Never connect
    // the routed socket to its server, keeping ws:// and wss:// fail-closed.
    await context.routeWebSocket(/.*/, async (websocket) => {
      blocked.push({ kind: "websocket", url: websocket.url() });
      await websocket.close({ code: 1008, reason: "carousel network disabled" });
    });

    const page = await context.newPage();
    await page.goto(args.url, { waitUntil: "domcontentloaded", timeout: 30_000 });
    // Page-authored JavaScript is disabled. This trusted controller selects
    // the slide and performs readiness checks from outside the page runtime.
    await page.evaluate(async (slideId) => {
      document.body.classList.add("export");
      document.body.dataset.exportSlide = slideId;
      const slides = Array.from(document.querySelectorAll(".slide[data-slide]"));
      const selected = slides.filter((slide) => slide.getAttribute("data-slide") === slideId);
      if (selected.length !== 1) throw new Error(`expected one selected slide, found ${selected.length}`);
      for (const slide of slides) {
        const active = slide === selected[0];
        slide.hidden = !active;
        if (active) slide.style.removeProperty("display");
        else slide.style.setProperty("display", "none", "important");
      }
      await document.fonts.ready;
      await Promise.all(Array.from(document.fonts).map((font) => font.load()));
      const images = Array.from(document.images).filter((image) => !image.closest("[hidden]"));
      await Promise.all(images.map((image) => image.decode()));
      if (images.some((image) => !image.complete || image.naturalWidth === 0)) {
        throw new Error("one or more selected-slide images failed to load");
      }
      document.documentElement.dataset.carouselReady = "true";
    }, args.slide);
    if (Number(args["wait-ms"]) > 0) await page.waitForTimeout(Number(args["wait-ms"]));
    if (blocked.length) throw new Error(`blocked ${blocked.length} non-local network connection(s)`);
    await page.screenshot({ path: args.output, type: "png", fullPage: false });
  } finally {
    await context.close();
    await browser.close();
  }
}

try {
  await main();
} catch (error) {
  console.error(`renderer error: ${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
}
