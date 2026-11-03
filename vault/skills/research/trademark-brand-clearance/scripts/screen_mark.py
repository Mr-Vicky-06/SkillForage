#!/usr/bin/env python3
"""Trademark Name Collision & Phonetic Clearance Screener."""
import sys
import json

def soundex(name):
    # Basic soundex approximation
    name = name.upper()
    codes = {"B": "1", "F": "1", "P": "1", "V": "1", "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2", "D": "3", "T": "3", "L": "4", "M": "5", "N": "5", "R": "6"}
    res = [name[0]]
    for ch in name[1:]:
        c = codes.get(ch, "")
        if c and c != res[-1]:
            res.append(c)
    return ("".join(res) + "000")[:4]

def screen_brand(name, registered_marks):
    sx = soundex(name)
    collisions = []
    for reg in registered_marks:
        if soundex(reg) == sx or name.lower() in reg.lower() or reg.lower() in name.lower():
            collisions.append(reg)
    return {"brand_candidate": name, "phonetic_collisions": collisions, "clearance_status": "CLEAR" if not collisions else "RISK_OF_CONFUSION"}

def main():
    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"candidate": "SkillForge", "registered": ["SkillForce", "ToolForge", "AppForge"]}
    res = screen_brand(payload.get("candidate", "SkillForge"), payload.get("registered", []))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
