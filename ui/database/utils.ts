// database/utils.ts  - new helper (leave the array-based select() in place if you like)
import type { Database } from './schema';
import { getDuckDB } from './duckdb';

/* ────── shared helpers ────── */
type TableName = keyof Database;                 // "events" | "results"
type Col<T extends TableName> = Extract<keyof Database[T], string>;

export interface QueryOpts<T extends TableName> {
    where?: Partial<Record<Col<T>, unknown>>;
    orderBy?: Col<T> | { column: Col<T>; desc?: boolean };
    limit?: number;
}

/* ────── object-based column spec ──────
 *  - key   = column in the table
 *  - value = either `true`  (keep the same name)
 *            or a string    (alias → SELECT "col" AS "alias")
 */
type ColSpec<T extends TableName> = Partial<
    Record<Col<T>, true | string>
>;

/* Map the spec to the *result* type
 *  - alias string → becomes property key
 *  - `true`       → keeps original column name
 */
type Mapped<
    T extends TableName,
    S extends ColSpec<T>
> = {
        [K in keyof S as S[K] extends string ? S[K] : K]:
        Database[T][K & keyof Database[T]];
    };

/* ────── the helper ────── */
export async function select<
    T extends TableName,
    S extends ColSpec<T>,
>(
    table: T,
    columns: S,
    opts: QueryOpts<T> = {}
): Promise<Mapped<T, S>[]> {
    /* 1. Build SELECT list */
    const colFragments = Object.entries(columns).map(([k, v]) =>
        v === true ? `"${k}"` : `"${k}" AS "${v}"`
    );
    if (colFragments.length === 0)
        throw new Error('You must select at least one column');

    /* 2. WHERE / ORDER / LIMIT (same as before) */
    const whereKeys = opts.where ? Object.keys(opts.where) as Col<T>[] : [];
    const whereSQL = whereKeys.length
        ? 'WHERE ' + whereKeys.map(k => `"${k}" = $${k}`).join(' AND ')
        : '';
    const params = opts.where ?? {};

    const orderSQL = opts.orderBy
        ? (() => {
            const o = typeof opts.orderBy === 'string'
                ? { column: opts.orderBy }
                : opts.orderBy;
            return `ORDER BY "${o.column}"${o.desc ? ' DESC' : ''}`;
        })()
        : '';

    const limitSQL = opts.limit ? `LIMIT ${opts.limit}` : '';

    const sql = `SELECT ${colFragments.join(', ')} FROM ${table} ${whereSQL} ${orderSQL} ${limitSQL}`.trim();

    /* 3. Execute via DuckDB */
    const db = await getDuckDB();
    const conn = await db.connect();
    try {
        const reader = await conn.runAndReadAll(sql, params);
        return reader.getRowObjectsJson() as Mapped<T, S>[];
    } finally {
        conn.closeSync();
    }
}
