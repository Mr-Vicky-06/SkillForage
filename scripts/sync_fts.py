"""Syncs all skills in skills table into skill_fts FTS5 table."""

import sqlite3
from pathlib import Path

DB_PATH = Path("data/registry.db")

def sync_fts():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("DELETE FROM skill_fts;")
        skills = conn.execute("SELECT id, name, description, category, subcategory FROM skills;").fetchall()
        for s in skills:
            skill_id = s["id"]
            # get tags
            tags_rows = conn.execute("SELECT tag FROM skill_tags WHERE skill_id = ?", (skill_id,)).fetchall()
            tags_str = " ".join(r["tag"] for r in tags_rows)
            # get triggers
            trig_rows = conn.execute("SELECT trigger FROM skill_triggers WHERE skill_id = ?", (skill_id,)).fetchall()
            trig_str = " ".join(r["trigger"] for r in trig_rows)
            # get technologies
            tech_rows = conn.execute("SELECT technology FROM skill_technologies WHERE skill_id = ?", (skill_id,)).fetchall()
            tech_str = " ".join(r["technology"] for r in tech_rows)

            conn.execute("""
                INSERT INTO skill_fts (skill_id, name, description, category, subcategory, triggers, tags, technologies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill_id,
                s["name"],
                s["description"] or "",
                s["category"] or "",
                s["subcategory"] or "",
                trig_str,
                tags_str,
                tech_str
            ))
    
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM skill_fts")
    fts_count = cur.fetchone()[0]
    conn.close()
    print(f"FTS5 synchronized successfully. Total indexed skills: {fts_count}")

if __name__ == "__main__":
    sync_fts()

