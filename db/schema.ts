import { pgTable, serial, text, jsonb, timestamp, index } from 'drizzle-orm/pg-core';

export const records = pgTable('operations_records', {
  id: serial('id').primaryKey(),
  kind: text('kind').notNull(),
  data: jsonb('data').notNull().default({}),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
}, table => [index('operations_records_kind_idx').on(table.kind)]);
