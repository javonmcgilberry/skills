#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import path from "node:path";

const corpusPath = path.join(process.cwd(), ".research", "corpus.json");
const corpus = JSON.parse(await readFile(corpusPath, "utf8"));
const [command, ...values] = process.argv.slice(2);

if (command === "list") {
  for (const source of corpus) {
    console.log(`${source.id} | ${source.date} | ${source.title}`);
  }
} else if (command === "search") {
  const query = values.join(" ").trim().toLowerCase();
  if (!query) {
    throw new Error("Usage: node research.mjs search <query>");
  }
  const terms = query.split(/[^a-z0-9]+/u).filter(term => term.length > 2);
  const matches = corpus
    .map((source, order) => {
      const title = source.title.toLowerCase();
      const body = source.content.toLowerCase();
      const score = terms.reduce(
        (total, term) =>
          total
          + (title.includes(term) ? 3 : 0)
          + (body.includes(term) ? 1 : 0),
        0
      );
      return { source, score, order };
    })
    .filter(match => match.score > 0)
    .sort((left, right) => right.score - left.score || left.order - right.order)
    .slice(0, 6);

  if (matches.length === 0) {
    console.log("No matching sources.");
  } else {
    for (const match of matches) {
      console.log(
        `${match.source.id} | ${match.source.date} | ${match.source.title}`
      );
    }
  }
} else if (command === "read") {
  const sourceId = values[0];
  const source = corpus.find(candidate => candidate.id === sourceId);
  if (!source) {
    throw new Error(`Unknown source ID: ${sourceId ?? ""}`);
  }
  console.log(`[${source.id}]`);
  console.log(`Title: ${source.title}`);
  console.log(`Date: ${source.date}`);
  console.log("");
  console.log(source.content);
} else {
  throw new Error(
    "Usage: node research.mjs <list | search <query> | read <source-id>>"
  );
}
