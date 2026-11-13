CREATE TABLE "operations_records" (
	"id" serial PRIMARY KEY,
	"kind" text NOT NULL,
	"data" jsonb DEFAULT '{}' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE INDEX "operations_records_kind_idx" ON "operations_records" ("kind");