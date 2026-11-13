import { getDatabase } from '@netlify/database';
import { HttpError } from '../web/services.mjs';
import { drizzle } from 'drizzle-orm/netlify-db';
import { eq, and, sql } from 'drizzle-orm';
import { records } from './schema.ts';
export const db = drizzle();
export const repository = {
  async list(kind) {
    const rows = await db.select().from(records).where(eq(records.kind, kind));
    return rows.map(row => ({ ...row.data, id: row.id, created_at: row.createdAt, updated_at: row.updatedAt }));
  },
  async create(kind, data) {
    const [row] = await db.insert(records).values({ kind, data }).returning();
    return { ...row.data, id: row.id };
  },
  async update(kind, id, data) {
    const [row] = await db.update(records).set({ data, updatedAt: new Date() }).where(and(eq(records.kind, kind), eq(records.id, id))).returning();
    return row ? { ...row.data, id: row.id } : null;
  },
  async remove(kind, id) {
    return db.delete(records).where(and(eq(records.kind, kind), eq(records.id, id))).returning();
  },
  async healthy() { await db.select({ id: records.id }).from(records).limit(1); return true; },
  async rejectApproval(id, reason) {
    const rows = await db.update(records).set({ data: sql`${records.data} || ${JSON.stringify({ status: 'REJECTED', rejection_reason: reason })}::jsonb`, updatedAt: new Date() }).where(and(eq(records.id, id), eq(records.kind, 'approval-requests'), sql`${records.data}->>'status' = 'PENDING'`)).returning();
    if (!rows.length) throw new HttpError(409, 'This request has already been reviewed.');
  },
  async applyOperation(operation, approvalId = null) {
    const client = await getDatabase().pool.connect();
    try {
      await client.query('BEGIN');
      if (approvalId) {
        const approval = await client.query('SELECT data FROM operations_records WHERE id = $1 AND kind = $2 FOR UPDATE', [approvalId, 'approval-requests']);
        if (!approval.rows[0] || approval.rows[0].data.status !== 'PENDING') throw new HttpError(409, 'This request has already been reviewed.');
      }
      let data;
      let recordId = operation.id;
      if (operation.action === 'create') {
        const inserted = await client.query('INSERT INTO operations_records (kind, data) VALUES ($1, $2) RETURNING id', [operation.kind, JSON.stringify(operation.changes)]);
        data = operation.changes;
        recordId = inserted.rows[0].id;
      } else {
        const target = await client.query('SELECT data FROM operations_records WHERE id = $1 AND kind = $2 FOR UPDATE', [operation.id, operation.kind]);
        if (!target.rows[0]) throw new HttpError(404, 'Record not found.');
        data = target.rows[0].data;
        if (operation.action === 'dispatch') {
          if (!Number.isInteger(operation.quantity) || operation.quantity <= 0 || operation.quantity > Number(data.quantity_available || 0)) throw new HttpError(400, 'Dispatch quantity exceeds available stock or is invalid.');
          data.quantity_available = Number(data.quantity_available) - operation.quantity;
          data.quantity_allocated = Number(data.quantity_allocated || 0) + operation.quantity;
        } else Object.assign(data, operation.changes);
        await client.query('UPDATE operations_records SET data = $1, updated_at = now() WHERE id = $2', [JSON.stringify(data), recordId]);
      }
      await client.query('INSERT INTO operations_records (kind, data) VALUES ($1, $2)', ['audit-logs', JSON.stringify({ action: operation.action, details: operation, timestamp: new Date().toISOString() })]);
      if (approvalId) await client.query("UPDATE operations_records SET data = data || '{\"status\":\"APPROVED\"}'::jsonb, updated_at = now() WHERE id = $1", [approvalId]);
      await client.query('COMMIT');
      return { ...data, id: recordId };
    } catch (error) { await client.query('ROLLBACK'); throw error; }
    finally { client.release(); }
  },
};
