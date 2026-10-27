#!/usr/bin/env node
// Fails when a tracked Markdown file names something the repository does not have: a repository path, a relative link or its anchor,
// or a pnpm script that no package.json defines. `pnpm docs:check` runs it, and `pnpm check` runs that.
// Usage: node scripts/docs-check.mts      prints one line per problem and exits 1 when there is one.
//
// A path is checked when it sits in code (a code span or a fenced block), has a slash, and starts at a tracked top-level entry of the
// repository, or of the document's own directory. A path Git ignores, such as `apps/server/.env.local`, is not checked, and neither is
// a path with a placeholder (`<site-id>/forms`), so write the placeholder when a path is outside the repository.
//
// A pnpm command is checked when it sits in code. `pnpm <script>` and `pnpm run <script>` name a script of the root package.json, or of
// the workspace package the document lives in. `pnpm --filter <package> <script>` names a script of that package, by name or directory.
// `pnpm --recursive <script>` names a script of any package. pnpm's own commands, such as `install` and `exec`, are not checked.
import {execFileSync} from 'node:child_process';
import {existsSync, readFileSync, readdirSync, statSync} from 'node:fs';
import {dirname, join, normalize, relative} from 'node:path';

export type Problem = {
  file: string;
  line: number;
  kind: 'path' | 'link' | 'anchor' | 'script';
  message: string;
};

export type WorkspacePackage = {
  name: string;
  dir: string;
  scripts: ReadonlySet<string>;
};

// What the repository has: its tracked top-level entries, its packages (the root is dir '.'), and the paths Git ignores.
export type Facts = {
  topLevel: ReadonlySet<string>;
  packages: readonly WorkspacePackage[];
  ignored: (path: string) => boolean;
};

// History, kept as it was released. Its compare links point at tags, not files.
const EXCLUDED = new Set(['apps/cdn/CHANGELOG.md']);

// pnpm's own commands. Any other first word is a script.
const PNPM_COMMANDS = new Set([
  'add',
  'approve-builds',
  'audit',
  'config',
  'create',
  'deploy',
  'dlx',
  'env',
  'exec',
  'fetch',
  'help',
  'i',
  'import',
  'init',
  'install',
  'licenses',
  'link',
  'list',
  'ls',
  'outdated',
  'pack',
  'patch',
  'patch-commit',
  'prune',
  'publish',
  'rebuild',
  'remove',
  'rm',
  'setup',
  'store',
  'unlink',
  'up',
  'update',
  'why',
]);

type Line = {n: number; text: string; fenced: boolean};

function linesOf(source: string): Line[] {
  let fenced = false;

  return source.split('\n').map((text, i) => {
    const fence = /^\s*(```|~~~)/.test(text);
    const line = {n: i + 1, text, fenced: fenced || fence};

    if (fence) fenced = !fenced;

    return line;
  });
}

const spansOf = (text: string): string[] =>
  [...text.matchAll(/`([^`]+)`/g)].map((m) => m[1]);

// The code of a line: the whole line in a fenced block, else its code spans.
const codeOf = (line: Line): string[] =>
  line.fenced ? [line.text] : spansOf(line.text);

// GitHub's anchor for a heading: lower case, without punctuation but hyphens and underscores, spaces as hyphens, a repeat numbered.
export function anchorsOf(source: string): Set<string> {
  const seen = new Map<string, number>();
  const anchors = new Set<string>();

  for (const line of linesOf(source)) {
    for (const m of line.text.matchAll(/<a\s+(?:id|name)="([^"]+)"/g))
      anchors.add(m[1]);
    const heading = !line.fenced && /^#{1,6}\s+(.*)$/.exec(line.text);

    if (!heading) continue;
    const slug = heading[1]
      .replace(/`/g, '')
      .trim()
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s_-]/gu, '')
      .replace(/\s/g, '-');
    const count = seen.get(slug) ?? 0;

    anchors.add(count ? `${slug}-${count}` : slug);
    seen.set(slug, count + 1);
  }

  return anchors;
}

function checkPaths(
  file: string,
  line: Line,
  root: string,
  facts: Facts,
  problems: Problem[]
): void {
  const docDir = dirname(file);

  for (const code of codeOf(line)) {
    for (const raw of code.split(/[\s"'`(),;=[\]|]+/)) {
      const token = raw.replace(/[.:]+$/, '');

      if (
        !token.includes('/') ||
        /[<>*{}$~:@#?]/.test(token) ||
        token.startsWith('/') ||
        token.includes('//')
      )
        continue;
      // From the document's directory when the token starts there (../, or an entry of that directory), else from the root, where
      // commands run.
      const local =
        token.startsWith('../') ||
        (!token.startsWith('./') &&
          docDir !== '.' &&
          existsSync(join(root, docDir, token.split('/')[0])));
      const path = normalize(local ? join(docDir, token) : token);
      const first = path.split('/')[0];

      if (path.startsWith('..') || !facts.topLevel.has(first)) continue;
      if (!existsSync(join(root, path)) && !facts.ignored(path))
        problems.push({
          file,
          line: line.n,
          kind: 'path',
          message: `${token} does not exist`,
        });
    }
  }
}

function checkLinks(
  file: string,
  line: Line,
  root: string,
  problems: Problem[]
): void {
  if (line.fenced) return;
  const text = line.text.replace(/`[^`]*`/g, '');

  for (const m of text.matchAll(/\]\(([^)\s]+)\)/g)) {
    const target = m[1];

    if (/^[a-z]+:/i.test(target)) continue;
    const [path, anchor] = target.split('#');
    const resolved = path ? normalize(join(dirname(file), path)) : file;

    if (resolved.startsWith('..')) {
      problems.push({
        file,
        line: line.n,
        kind: 'link',
        message: `${target} leaves the repository, so it resolves only on a machine that has it`,
      });
      continue;
    }
    if (!existsSync(join(root, resolved))) {
      problems.push({
        file,
        line: line.n,
        kind: 'link',
        message: `${target} does not resolve`,
      });
      continue;
    }
    if (anchor === undefined || statSync(join(root, resolved)).isDirectory())
      continue;
    if (!anchorsOf(readFileSync(join(root, resolved), 'utf8')).has(anchor))
      problems.push({
        file,
        line: line.n,
        kind: 'anchor',
        message: `${target} names no heading or anchor in ${resolved}`,
      });
  }
}

// The package a --filter value names, by package name or by directory.
const packageNamed = (facts: Facts, filter: string) =>
  facts.packages.find(
    (p) => p.name === filter || p.dir === normalize(filter.replace(/^\.\//, ''))
  );

// The workspace package that owns a document: the deepest package directory that contains it, else the root.
function ownerOf(facts: Facts, file: string): WorkspacePackage | undefined {
  return facts.packages
    .filter((p) => p.dir === '.' || file.startsWith(`${p.dir}/`))
    .sort((a, b) => b.dir.length - a.dir.length)[0];
}

// A `pnpm [flags] [run] <script>` in code. The words after pnpm run to the end of the code, a comment, or the next command.
function checkScripts(
  file: string,
  line: Line,
  facts: Facts,
  problems: Problem[]
): void {
  const root = facts.packages.find((p) => p.dir === '.');
  const owner = ownerOf(facts, file);

  for (const code of codeOf(line)) {
    for (const command of code.split(/&&|\|\||;|\||#/)) {
      const words = command.trim().split(/\s+/);
      const at = words.indexOf('pnpm');

      if (at === -1 || (at > 0 && !/^(npx|corepack|sudo)$/.test(words[0])))
        continue;
      let filter: string | undefined;
      let recursive = false;
      let i = at + 1;

      for (; i < words.length && words[i].startsWith('-'); i++) {
        if (words[i] === '--filter' || words[i] === '-F') filter = words[++i];
        else if (words[i].startsWith('--filter='))
          filter = words[i].slice('--filter='.length);
        else if (/^(-r|--recursive)$/.test(words[i])) recursive = true;
        else if (words[i] === '-C' || words[i] === '--dir') i++;
      }
      if (words[i] === 'run') i++;
      const script = words[i];

      if (!script || !/^[a-z][\w:.-]*$/.test(script)) continue;
      if (words[i - 1] !== 'run' && PNPM_COMMANDS.has(script)) continue;

      if (filter !== undefined) {
        const target = packageNamed(facts, filter);

        if (!target)
          problems.push({
            file,
            line: line.n,
            kind: 'script',
            message: `pnpm --filter ${filter} names no workspace package`,
          });
        else if (!target.scripts.has(script))
          problems.push({
            file,
            line: line.n,
            kind: 'script',
            message: `${target.name} has no script ${script}`,
          });
        continue;
      }
      const known = recursive
        ? facts.packages.some((p) => p.scripts.has(script))
        : Boolean(root?.scripts.has(script) || owner?.scripts.has(script));

      if (!known)
        problems.push({
          file,
          line: line.n,
          kind: 'script',
          message: `pnpm ${script} is not a script of ${recursive ? 'any package' : owner && owner !== root ? `the root or ${owner.name}` : 'the root package.json'}`,
        });
    }
  }
}

export function checkDocs({
  root,
  files,
  facts,
}: {
  root: string;
  files: readonly string[];
  facts: Facts;
}): Problem[] {
  const problems: Problem[] = [];

  for (const file of files) {
    for (const line of linesOf(readFileSync(join(root, file), 'utf8'))) {
      checkPaths(file, line, root, facts, problems);
      checkLinks(file, line, root, problems);
      checkScripts(file, line, facts, problems);
    }
  }

  return problems;
}

// The workspace's package directories, from pnpm-workspace.yaml entries such as 'apps/*' or 'scripts'.
function packageDirs(root: string): string[] {
  const workspace = join(root, 'pnpm-workspace.yaml');
  const globs = existsSync(workspace)
    ? [
        ...readFileSync(workspace, 'utf8').matchAll(
          /^\s*-\s*['"]?([^'"\s]+)['"]?\s*$/gm
        ),
      ].map((m) => m[1])
    : [];

  return globs.flatMap((glob) => {
    if (!glob.endsWith('/*')) return [glob];
    const parent = glob.slice(0, -2);

    return existsSync(join(root, parent))
      ? readdirSync(join(root, parent)).map((entry) => join(parent, entry))
      : [];
  });
}

function readPackage(root: string, dir: string): WorkspacePackage | undefined {
  const manifest = join(root, dir, 'package.json');

  if (!existsSync(manifest)) return undefined;
  const json = JSON.parse(readFileSync(manifest, 'utf8')) as {
    name?: string;
    scripts?: Record<string, string>;
  };

  return {
    name: json.name ?? dir,
    dir,
    scripts: new Set(Object.keys(json.scripts ?? {})),
  };
}

// The repository's facts, read from Git and the package manifests.
export function repoFacts(root: string): Facts {
  const tracked = execFileSync('git', ['ls-files'], {
    cwd: root,
    encoding: 'utf8',
  })
    .split('\n')
    .filter(Boolean);
  const packages = ['.', ...packageDirs(root)]
    .map((dir) => readPackage(root, dir))
    .filter((p): p is WorkspacePackage => p !== undefined);
  const ignored = (path: string): boolean => {
    try {
      execFileSync('git', ['check-ignore', '--quiet', '--no-index', path], {
        cwd: root,
      });

      return true;
    } catch {
      return false;
    }
  };

  return {
    topLevel: new Set(tracked.map((f) => f.split('/')[0])),
    packages,
    ignored,
  };
}

export const trackedDocs = (root: string): string[] =>
  execFileSync('git', ['ls-files', '*.md'], {cwd: root, encoding: 'utf8'})
    .split('\n')
    .filter((f) => f && !EXCLUDED.has(f));

if (
  process.argv[1] &&
  relative(process.cwd(), process.argv[1]).endsWith('scripts/docs-check.mts')
) {
  const root = join(import.meta.dirname, '..');
  const problems = checkDocs({
    root,
    files: trackedDocs(root),
    facts: repoFacts(root),
  });

  for (const p of problems)
    process.stdout.write(`${p.file}:${p.line} ${p.kind}: ${p.message}\n`);
  if (problems.length) process.exit(1);
}
