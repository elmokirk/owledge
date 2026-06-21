import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const EDGE_TYPES = new Set([
  "relates_to",
  "depends_on",
  "supersedes",
  "superseded_by",
  "derived_from",
  "evidence_for",
  "implements",
  "blocks",
  "unblocks",
  "validates",
  "contradicts",
  "similar_to",
  "shared_lesson_for",
]);

const MEMORY_PATHS = [
  "PROJECT_CONTEXT.md",
  "USER_CONTEXT.md",
  "agent-memory/canonical",
  "agent-memory/compiled",
  "agent-memory/patterns",
  "agent-memory/lessons",
  "agent-memory/ideas",
  "agent-memory/decisions",
  "agent-memory/evidence",
  "agent-memory/handoffs",
  "agent-memory/sessions",
  "agent-memory/pi-agent/reports",
  "agent-memory/pi-agent/parallels",
  "agent-memory/pi-agent/trends",
  "agent-memory/pi-agent/recurring-errors",
  "agent-memory/pi-agent/concepts",
  "agent-memory/pi-agent/red-team",
  "agent-memory/pi-agent/evaluations",
  "agent-memory/pi-agent/scorecards",
  "global-memory/preferences",
  "global-memory/goals",
  "global-memory/daily",
  "global-memory/tasks",
  "global-memory/ideas",
  "global-memory/research",
  "global-memory/patterns",
  "global-memory/coach",
];

const STOP_WORDS = new Set([
  "a",
  "an",
  "and",
  "as",
  "for",
  "in",
  "is",
  "it",
  "of",
  "on",
  "or",
  "the",
  "to",
  "with",
]);

type JsonSchemaProperty = {
  type?: string;
  enum?: string[];
  pattern?: string;
  minLength?: number;
  minimum?: number;
  maximum?: number;
};

type JsonSchema = {
  required?: string[];
  properties?: Record<string, JsonSchemaProperty>;
};

type Issue = {
  path: string;
  message: string;
};

type MemoryRecord = {
  sourcePath: string;
  sourceHash: string;
  metadata: Record<string, unknown>;
  body: string;
};

type QueryFixture = {
  query: string;
  limit?: number;
  expected_memory_ids?: string[];
};

type RetrievalFixture = {
  name?: string;
  queries?: QueryFixture[];
};

type Options = {
  root: string;
  strict: boolean;
  json: boolean;
  fixture?: string;
  query?: string;
  limit: number;
};

function usage(): string {
  return [
    "Usage: owledge-lint [--root <path>] [--strict] [--fixture <path>] [--query <text>] [--limit <n>] [--json]",
    "",
    "Checks Owledge Markdown frontmatter and runs optional retrieval fixtures.",
  ].join("\n");
}

function parseArgs(argv: string[]): Options {
  const options: Options = {
    root: process.cwd(),
    strict: false,
    json: false,
    limit: 5,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      console.log(usage());
      process.exit(0);
    }
    if (arg === "--strict") {
      options.strict = true;
    } else if (arg === "--json") {
      options.json = true;
    } else if (arg === "--root") {
      options.root = argv[++index] ?? options.root;
    } else if (arg === "--fixture") {
      options.fixture = argv[++index];
    } else if (arg === "--query") {
      options.query = argv[++index];
    } else if (arg === "--limit") {
      options.limit = Number.parseInt(argv[++index] ?? "5", 10);
    } else {
      throw new Error(`Unknown argument: ${arg}\n${usage()}`);
    }
  }
  options.root = path.resolve(options.root);
  return options;
}

function schemaPath(): string {
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "../schemas/core-frontmatter.schema.json");
}

function loadSchema(): JsonSchema {
  return JSON.parse(fs.readFileSync(schemaPath(), "utf8")) as JsonSchema;
}

function parseInlineArray(value: string): unknown[] {
  const inner = value.slice(1, -1).trim();
  if (!inner) return [];
  return inner.split(",").map((item) => parseScalar(item.trim()));
}

function parseScalar(raw: string): unknown {
  const value = raw.trim();
  if (!value) return "";
  if (value === "[]") return [];
  if (value.startsWith("[") && value.endsWith("]")) return parseInlineArray(value);
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    return value.slice(1, -1);
  }
  if (value === "true") return true;
  if (value === "false") return false;
  if (/^-?\d+(\.\d+)?$/.test(value)) return Number(value);
  return value;
}

function parseFrontmatter(text: string): { hasFrontmatter: boolean; metadata: Record<string, unknown>; body: string } {
  const normalized = text.replace(/^\uFEFF/, "");
  const lines = normalized.split(/\r?\n/);
  if (lines[0] !== "---") {
    return { hasFrontmatter: false, metadata: {}, body: normalized };
  }
  const end = lines.findIndex((line, index) => index > 0 && line === "---");
  if (end < 0) {
    return { hasFrontmatter: false, metadata: {}, body: normalized };
  }
  const metadata: Record<string, unknown> = {};
  let currentKey: string | undefined;
  let currentListObject: Record<string, unknown> | undefined;
  for (const rawLine of lines.slice(1, end)) {
    if (!rawLine.trim()) continue;
    const trimmed = rawLine.trim();
    if (trimmed.startsWith("- ") && currentKey) {
      if (!Array.isArray(metadata[currentKey])) metadata[currentKey] = [];
      const list = metadata[currentKey] as unknown[];
      const item = trimmed.slice(2).trim();
      if (item.includes(":")) {
        const [key, ...rest] = item.split(":");
        currentListObject = { [key.trim()]: parseScalar(rest.join(":")) };
        list.push(currentListObject);
      } else {
        currentListObject = undefined;
        list.push(parseScalar(item));
      }
      continue;
    }
    if (rawLine.startsWith("    ") && currentListObject && trimmed.includes(":")) {
      const [key, ...rest] = trimmed.split(":");
      currentListObject[key.trim()] = parseScalar(rest.join(":"));
      continue;
    }
    if (!rawLine.startsWith(" ") && rawLine.includes(":")) {
      const [key, ...rest] = rawLine.split(":");
      currentKey = key.trim();
      currentListObject = undefined;
      metadata[currentKey] = parseScalar(rest.join(":"));
    }
  }
  return {
    hasFrontmatter: true,
    metadata,
    body: lines.slice(end + 1).join("\n").trimStart(),
  };
}

function walkMarkdownFiles(target: string): string[] {
  if (!fs.existsSync(target)) return [];
  const stat = fs.statSync(target);
  if (stat.isFile()) return target.endsWith(".md") ? [target] : [];
  const results: string[] = [];
  for (const entry of fs.readdirSync(target, { withFileTypes: true })) {
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    const child = path.join(target, entry.name);
    if (entry.isDirectory()) {
      results.push(...walkMarkdownFiles(child));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      results.push(child);
    }
  }
  return results;
}

function memoryMarkdownFiles(root: string): string[] {
  const seen = new Set<string>();
  for (const rel of MEMORY_PATHS) {
    for (const file of walkMarkdownFiles(path.join(root, rel))) {
      seen.add(path.resolve(file));
    }
  }
  return [...seen].sort();
}

function relativePath(root: string, file: string): string {
  return path.relative(root, file).replaceAll(path.sep, "/");
}

function sha256(text: string): string {
  return crypto.createHash("sha256").update(text).digest("hex");
}

function checkType(value: unknown, expected: string): boolean {
  if (expected === "array") return Array.isArray(value);
  if (expected === "number") return typeof value === "number" && Number.isFinite(value);
  if (expected === "string") return typeof value === "string";
  if (expected === "object") return typeof value === "object" && value !== null && !Array.isArray(value);
  return true;
}

function validateMetadata(meta: Record<string, unknown>, rel: string, schema: JsonSchema): Issue[] {
  const issues: Issue[] = [];
  for (const key of schema.required ?? []) {
    if (!(key in meta)) issues.push({ path: rel, message: `missing ${key}` });
  }
  for (const [key, property] of Object.entries(schema.properties ?? {})) {
    if (!(key in meta)) continue;
    const value = meta[key];
    if (property.type && !checkType(value, property.type)) {
      issues.push({ path: rel, message: `${key} must be ${property.type}` });
    }
    if (property.enum && typeof value === "string" && !property.enum.includes(value)) {
      issues.push({ path: rel, message: `invalid ${key}=${value}` });
    }
    if (property.pattern && typeof value === "string" && !new RegExp(property.pattern).test(value)) {
      issues.push({ path: rel, message: `${key} must match ${property.pattern}` });
    }
    if (property.minLength && typeof value === "string" && value.length < property.minLength) {
      issues.push({ path: rel, message: `${key} must not be empty` });
    }
    if (typeof value === "number" && property.minimum !== undefined && value < property.minimum) {
      issues.push({ path: rel, message: `${key} must be >= ${property.minimum}` });
    }
    if (typeof value === "number" && property.maximum !== undefined && value > property.maximum) {
      issues.push({ path: rel, message: `${key} must be <= ${property.maximum}` });
    }
  }
  const edges = meta.edges;
  if (edges !== undefined) {
    if (!Array.isArray(edges)) {
      issues.push({ path: rel, message: "edges must be an array" });
    } else {
      edges.forEach((edge, index) => {
        if (!edge || typeof edge !== "object" || Array.isArray(edge)) {
          issues.push({ path: rel, message: `edge ${index} must be an object` });
          return;
        }
        const typedEdge = edge as Record<string, unknown>;
        if (typeof typedEdge.type !== "string" || !EDGE_TYPES.has(typedEdge.type)) {
          issues.push({ path: rel, message: `edge ${index} has invalid type` });
        }
        if (!typedEdge.target) {
          issues.push({ path: rel, message: `edge ${index} missing target` });
        }
      });
    }
  }
  if (meta.visibility === "shared") {
    if (meta.review_status !== "approved") {
      issues.push({ path: rel, message: "shared visibility requires review_status=approved" });
    }
    if (meta.sanitization_status !== "approved") {
      issues.push({ path: rel, message: "shared visibility requires sanitization_status=approved" });
    }
    if (!["public", "internal"].includes(String(meta.data_class ?? ""))) {
      issues.push({ path: rel, message: `shared visibility cannot export data_class=${String(meta.data_class ?? "")}` });
    }
  }
  return issues;
}

function loadRecords(root: string, schema: JsonSchema, strict: boolean): { records: MemoryRecord[]; issues: Issue[]; files: string[] } {
  const files = memoryMarkdownFiles(root);
  const records: MemoryRecord[] = [];
  const issues: Issue[] = [];
  const byId = new Map<string, string[]>();
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    const parsed = parseFrontmatter(text);
    const rel = relativePath(root, file);
    if (!parsed.hasFrontmatter) {
      if (strict) issues.push({ path: rel, message: "missing frontmatter" });
      continue;
    }
    if (!parsed.metadata.memory_id && !strict) continue;
    issues.push(...validateMetadata(parsed.metadata, rel, schema));
    if (typeof parsed.metadata.memory_id === "string") {
      const id = parsed.metadata.memory_id;
      byId.set(id, [...(byId.get(id) ?? []), rel]);
      if (parsed.metadata.data_class !== "confidential") {
        records.push({
          sourcePath: rel,
          sourceHash: sha256(text),
          metadata: parsed.metadata,
          body: parsed.body,
        });
      }
    }
  }
  for (const [id, paths] of byId.entries()) {
    if (paths.length > 1) {
      issues.push({ path: paths.join(", "), message: `duplicate memory_id ${id}` });
    }
  }
  const knownIds = new Set(byId.keys());
  for (const record of records) {
    const edges = record.metadata.edges;
    if (!Array.isArray(edges)) continue;
    for (const edge of edges) {
      if (!edge || typeof edge !== "object" || Array.isArray(edge)) continue;
      const typedEdge = edge as Record<string, unknown>;
      const target = String(typedEdge.target ?? "");
      if (target.startsWith("mem:") && typedEdge.external !== true && !knownIds.has(target)) {
        issues.push({ path: record.sourcePath, message: `missing internal edge target ${target}` });
      }
    }
  }
  return { records, issues, files };
}

function textForRecord(record: MemoryRecord): string {
  const meta = record.metadata;
  const fields = [
    meta.memory_id,
    meta.doc_type,
    meta.semantic_title,
    meta.summary,
    meta.concept_tags,
    meta.stack_tags,
    meta.problem_patterns,
    meta.architecture_patterns,
    meta.failure_modes,
    meta.reusable_lessons,
    record.body,
  ];
  return fields.flat().filter(Boolean).join(" ").toLowerCase();
}

function terms(query: string): string[] {
  return query
    .toLowerCase()
    .split(/[^a-z0-9:_-]+/)
    .filter((term) => term.length > 1 && !STOP_WORDS.has(term));
}

function search(records: MemoryRecord[], query: string, limit: number): Array<MemoryRecord & { score: number }> {
  const queryTerms = terms(query);
  return records
    .map((record) => {
      const haystack = textForRecord(record);
      let score = 0;
      for (const term of queryTerms) {
        const matches = haystack.match(new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g"));
        score += matches ? matches.length : 0;
      }
      return { ...record, score };
    })
    .filter((record) => record.score > 0)
    .sort((left, right) => right.score - left.score || left.sourcePath.localeCompare(right.sourcePath))
    .slice(0, limit);
}

function resolveInputPath(root: string, candidate: string): string {
  if (path.isAbsolute(candidate)) return candidate;
  const cwdPath = path.resolve(candidate);
  if (fs.existsSync(cwdPath)) return cwdPath;
  return path.resolve(root, candidate);
}

function runFixture(root: string, fixturePath: string, records: MemoryRecord[], defaultLimit: number) {
  const fixture = JSON.parse(fs.readFileSync(resolveInputPath(root, fixturePath), "utf8")) as RetrievalFixture;
  const queryResults = (fixture.queries ?? []).map((item) => {
    const limit = item.limit ?? defaultLimit;
    const results = search(records, item.query, limit);
    const found = new Set(results.map((record) => String(record.metadata.memory_id)));
    const expected = item.expected_memory_ids ?? [];
    const missing = expected.filter((id) => !found.has(id));
    return {
      query: item.query,
      limit,
      expected_memory_ids: expected,
      found_memory_ids: results.map((record) => record.metadata.memory_id),
      passed: missing.length === 0,
      missing,
    };
  });
  return {
    name: fixture.name ?? path.basename(fixturePath),
    passed: queryResults.every((result) => result.passed),
    total: queryResults.length,
    passedCount: queryResults.filter((result) => result.passed).length,
    results: queryResults,
  };
}

export async function main(argv: string[] = process.argv.slice(2)): Promise<number> {
  try {
    const options = parseArgs(argv);
    const schema = loadSchema();
    const { records, issues, files } = loadRecords(options.root, schema, options.strict);
    const fixture = options.fixture ? runFixture(options.root, options.fixture, records, options.limit) : undefined;
    const query = options.query ? search(records, options.query, options.limit) : undefined;
    const passed = issues.length === 0 && (!fixture || fixture.passed);
    const output = {
      root: options.root,
      passed,
      files: files.length,
      records: records.length,
      issues,
      fixture,
      query,
    };
    if (options.json) {
      console.log(JSON.stringify(output, null, 2));
    } else {
      console.log("Owledge TS adapter lint");
      console.log(`Root: ${options.root}`);
      console.log(`Markdown files: ${files.length}`);
      console.log(`Memory records: ${records.length}`);
      console.log(`Frontmatter: ${issues.length === 0 ? "passed" : `failed (${issues.length})`}`);
      for (const issue of issues.slice(0, 20)) {
        console.log(`- ${issue.path}: ${issue.message}`);
      }
      if (fixture) {
        console.log(`Retrieval fixture: ${fixture.passed ? "passed" : "failed"} (${fixture.passedCount}/${fixture.total})`);
        for (const result of fixture.results.filter((item) => !item.passed)) {
          console.log(`- ${result.query}: missing ${result.missing.join(", ")}`);
        }
      }
      if (query) {
        console.log("Query results:");
        for (const record of query) {
          console.log(`- ${record.score} ${String(record.metadata.memory_id)} ${record.sourcePath}`);
        }
      }
    }
    return passed ? 0 : 1;
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    return 2;
  }
}
