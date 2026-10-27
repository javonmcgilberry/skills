import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdirSync, mkdtempSync, rmSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {basename, dirname, join} from 'node:path';
import {after, test} from 'node:test';

import {anchorsOf, checkDocs, repoFacts, trackedDocs} from './docs-check.mts';

const root = mkdtempSync(join(tmpdir(), 'docs-check-'));

after(() => rmSync(root, {recursive: true, force: true}));

function write(path: string, content: string): void {
  mkdirSync(dirname(join(root, path)), {recursive: true});
  writeFileSync(join(root, path), content);
}

write(
  'package.json',
  JSON.stringify({scripts: {dev: 'x', 'db:up': 'x', check: 'x'}})
);
write('pnpm-workspace.yaml', "packages:\n  - 'apps/*'\n");
write(
  'apps/cdn/package.json',
  JSON.stringify({name: '@app/cdn', scripts: {'test:run': 'x', build: 'x'}})
);
write('apps/cdn/src/main.ts', '');
write('.gitignore', '.env.local\n');
write('docs/guide.md', '# Guide\n\n## Start the stack\n\nText.\n');
write(
  'apps/cdn/README.md',
  ['# CDN', '', 'Run `pnpm test:run` here, then `pnpm build`.', ''].join('\n')
);

const clean = [
  '# Readme',
  '',
  'Read [the guide](docs/guide.md#start-the-stack) and the [CDN](apps/cdn/README.md).',
  'The runtime starts in `apps/cdn/src/main.ts`, and secrets live in `apps/server/.env.local`.',
  'A placeholder such as `apps/<name>/src` is not checked, and neither is [Example](https://example.com).',
  '',
  '```bash',
  'pnpm install',
  'pnpm db:up && pnpm run dev',
  'pnpm --filter @app/cdn test:run',
  'pnpm --filter apps/cdn build',
  'pnpm exec playwright install chromium',
  '```',
  '',
].join('\n');

// One line per seeded break, each with the kind the check must report.
const seeded: [string, string][] = [
  ['The runtime starts in `apps/cdn/src/missing.ts`.', 'path'],
  ['Read [the guide](docs/gone.md).', 'link'],
  // Leaves the repository and comes back in, so the file exists on this machine and only the escape is wrong.
  [`Read [the plan](../../${basename(root)}/README.md).`, 'link'],
  ['Read [the guide](guide.md#no-such-heading).', 'anchor'],
  ['Run `pnpm db:seed`.', 'script'],
  ['Run `pnpm --filter @app/cdn test:watch`.', 'script'],
  ['Run `pnpm --filter @app/nope build`.', 'script'],
  ['Run `pnpm test:run` from the root.', 'script'],
];

write('README.md', clean);
write('docs/broken.md', ['# Broken', '', ...seeded.map(([l]) => l)].join('\n'));
execFileSync('git', ['init', '--quiet'], {cwd: root});
execFileSync('git', ['add', '.'], {cwd: root});

const facts = repoFacts(root);

test('a document that names only real things passes', () => {
  assert.deepEqual(
    checkDocs({
      root,
      files: ['README.md', 'apps/cdn/README.md', 'docs/guide.md'],
      facts,
    }),
    []
  );
});

test('every seeded break is caught, on its own line, as its kind', () => {
  const problems = checkDocs({root, files: ['docs/broken.md'], facts});

  assert.deepEqual(
    problems.map((p) => [p.line, p.kind]),
    seeded.map(([, kind], i) => [i + 3, kind])
  );
});

test('the tracked documents are the Markdown files Git tracks', () => {
  assert.deepEqual(trackedDocs(root).sort(), [
    'README.md',
    'apps/cdn/README.md',
    'docs/broken.md',
    'docs/guide.md',
  ]);
});

test('anchors follow GitHub: punctuation dropped, repeats numbered', () => {
  const anchors = anchorsOf(
    '# Run `pnpm dev`, then test\n## Limits\n## Limits\n'
  );

  assert.deepEqual(
    [...anchors],
    ['run-pnpm-dev-then-test', 'limits', 'limits-1']
  );
});
