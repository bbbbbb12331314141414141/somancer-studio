"""
Genre seed data for Sonmancer Studio.

Run with:
    python -m aimusic.utils.seed_genres
"""

from aimusic.db import SessionLocal
from aimusic.models.entities import Genre


GENRES = [
    # ── Root genres ──────────────────────────────────────────────
    {
        "name": "Rock",
        "description": "Guitar-driven music emphasising rhythm and energy.",
        "bpm_min": 80, "bpm_max": 160,
        "common_keys": ["E Major", "A Major", "D Major", "G Major"],
        "common_instruments": ["Electric Guitar", "Bass Guitar", "Drums", "Vocals"],
        "production_techniques": ["Distortion", "Power Chords", "Reverb"],
        "vocal_style": "Powerful, expressive",
    },
    {
        "name": "Electronic",
        "description": "Music produced primarily with electronic instruments and technology.",
        "bpm_min": 90, "bpm_max": 180,
        "common_keys": ["C Minor", "A Minor", "F Minor"],
        "common_instruments": ["Synthesizer", "Drum Machine", "Sampler"],
        "production_techniques": ["Sidechaining", "Automation", "Sound Design"],
        "vocal_style": "Processed or minimal",
    },
    {
        "name": "Hip-Hop",
        "description": "Rhythm-driven genre originating from African-American culture.",
        "bpm_min": 70, "bpm_max": 120,
        "common_keys": ["G Minor", "D Minor", "F Major"],
        "common_instruments": ["Drum Machine", "Sampler", "Bass"],
        "production_techniques": ["Sampling", "Boom-Bap", "Trap Hi-Hats"],
        "vocal_style": "Rap, melodic rap",
    },
    {
        "name": "Jazz",
        "description": "Improvisational genre rooted in blues, swing, and complex harmony.",
        "bpm_min": 60, "bpm_max": 280,
        "common_keys": ["Bb Major", "F Major", "Eb Major", "Ab Major"],
        "common_instruments": ["Piano", "Trumpet", "Saxophone", "Double Bass", "Drums"],
        "production_techniques": ["Improvisation", "Swing Feel", "Extended Chords"],
        "vocal_style": "Crooning, scat",
    },
    {
        "name": "R&B",
        "description": "Rhythm and blues with smooth vocals and groove-heavy production.",
        "bpm_min": 60, "bpm_max": 110,
        "common_keys": ["Bb Major", "F Major", "Db Major"],
        "common_instruments": ["Keyboards", "Bass", "Drums", "Horns"],
        "production_techniques": ["Groove Quantisation", "Layered Vocals", "Warm Bass"],
        "vocal_style": "Smooth, melismatic",
    },
    {
        "name": "Classical",
        "description": "Western art music following formal compositional traditions.",
        "bpm_min": 40, "bpm_max": 200,
        "common_keys": ["C Major", "G Major", "D Major", "A Major", "F Major"],
        "common_instruments": ["Strings", "Piano", "Woodwinds", "Brass", "Choir"],
        "production_techniques": ["Counterpoint", "Orchestration", "Dynamics"],
        "vocal_style": "Opera, choir",
    },
    # ── Rock subgenres ────────────────────────────────────────────
    {
        "name": "Hard Rock",
        "parent_name": "Rock",
        "description": "Heavy guitar riffs with aggressive rhythms.",
        "bpm_min": 100, "bpm_max": 160,
        "common_keys": ["E Major", "A Major", "D Minor"],
        "common_instruments": ["Distorted Guitar", "Heavy Bass", "Drums"],
        "production_techniques": ["Heavy Distortion", "Double Bass Drum"],
        "vocal_style": "Powerful, raw",
    },
    {
        "name": "Alternative Rock",
        "parent_name": "Rock",
        "description": "Experimental rock that emerged from the indie underground.",
        "bpm_min": 80, "bpm_max": 140,
        "common_keys": ["E Minor", "D Major", "G Major"],
        "common_instruments": ["Guitar", "Bass", "Drums"],
        "production_techniques": ["Lo-Fi Recording", "Jangly Guitar"],
        "vocal_style": "Introspective, melodic",
    },
    {
        "name": "Indie Rock",
        "parent_name": "Rock",
        "description": "Rock music released on independent labels with DIY ethos.",
        "bpm_min": 80, "bpm_max": 140,
        "common_keys": ["G Major", "D Major", "E Minor"],
        "common_instruments": ["Guitar", "Bass", "Drums", "Keyboards"],
        "production_techniques": ["Lo-Fi Aesthetic", "Jangly Guitars"],
        "vocal_style": "Conversational, earnest",
    },
    {
        "name": "Metal",
        "parent_name": "Rock",
        "description": "Loud, aggressive rock with heavily distorted guitars.",
        "bpm_min": 100, "bpm_max": 280,
        "common_keys": ["E Minor", "B Minor", "D Minor"],
        "common_instruments": ["Distorted Guitar", "Heavy Bass", "Double Bass Drums"],
        "production_techniques": ["Drop Tuning", "Palm Muting", "Blast Beats"],
        "vocal_style": "Screaming, singing, harsh vocals",
    },
    # ── Electronic subgenres ──────────────────────────────────────
    {
        "name": "House",
        "parent_name": "Electronic",
        "description": "Four-on-the-floor dance music originating in Chicago.",
        "bpm_min": 120, "bpm_max": 135,
        "common_keys": ["F Minor", "G Minor", "C Minor"],
        "common_instruments": ["Drum Machine", "Synthesizer", "Sampler"],
        "production_techniques": ["Four-on-the-Floor", "Sidechain Compression", "Filtering"],
        "vocal_style": "Soulful samples, hooks",
    },
    {
        "name": "Techno",
        "parent_name": "Electronic",
        "description": "Repetitive, machine-driven dance music from Detroit.",
        "bpm_min": 130, "bpm_max": 160,
        "common_keys": ["A Minor", "D Minor"],
        "common_instruments": ["Drum Machine", "Synthesizer", "Sequencer"],
        "production_techniques": ["Minimal Arrangement", "Industrial Textures"],
        "vocal_style": "Minimal or none",
    },
    {
        "name": "Ambient",
        "parent_name": "Electronic",
        "description": "Atmospheric music emphasising texture over rhythm.",
        "bpm_min": 60, "bpm_max": 100,
        "common_keys": ["D Major", "A Major", "E Major"],
        "common_instruments": ["Synthesizer", "Processed Guitar", "Field Recordings"],
        "production_techniques": ["Long Reverb", "Layered Pads", "Slow Modulation"],
        "vocal_style": "Processed, ethereal",
    },
    # ── Hip-Hop subgenres ─────────────────────────────────────────
    {
        "name": "Trap",
        "parent_name": "Hip-Hop",
        "description": "Southern hip-hop with 808 bass, hi-hat rolls, and dark production.",
        "bpm_min": 60, "bpm_max": 100,
        "common_keys": ["G Minor", "Eb Minor", "Bb Minor"],
        "common_instruments": ["808 Bass", "Hi-Hat Rolls", "Synth Pads"],
        "production_techniques": ["808 Bass", "Triplet Hi-Hats", "Layered Samples"],
        "vocal_style": "Rap, auto-tuned melodic",
    },
    {
        "name": "Neo-Soul",
        "parent_name": "R&B",
        "description": "Contemporary soul with jazz-influenced harmony and organic production.",
        "bpm_min": 60, "bpm_max": 100,
        "common_keys": ["Bb Major", "Eb Major", "F Minor"],
        "common_instruments": ["Rhodes Piano", "Bass", "Drums", "Guitar"],
        "production_techniques": ["Warm Mixing", "Layered Vocals", "Live Drums"],
        "vocal_style": "Smooth, emotional, melismatic",
    },
]


def seed_genres() -> None:
    """Insert seed genres into database if empty."""
    db = SessionLocal()
    try:
        existing = db.query(Genre).count()
        if existing > 0:
            print(f"Genres already seeded ({existing} records). Skipping.")
            return

        # Build name → id map for parent resolution
        name_to_id: dict[str, int] = {}

        # First pass: roots (no parent)
        for data in GENRES:
            if "parent_name" in data:
                continue
            genre = Genre(
                name=data["name"],
                description=data.get("description"),
                bpm_min=data.get("bpm_min"),
                bpm_max=data.get("bpm_max"),
                common_keys=data.get("common_keys", []),
                common_instruments=data.get("common_instruments", []),
                production_techniques=data.get("production_techniques", []),
                vocal_style=data.get("vocal_style"),
                sources=["Sonmancer Seed Data"],
            )
            db.add(genre)
        db.commit()

        # Refresh IDs
        for genre in db.query(Genre).all():
            name_to_id[genre.name] = genre.id

        # Second pass: children
        for data in GENRES:
            if "parent_name" not in data:
                continue
            parent_id = name_to_id.get(data["parent_name"])
            if not parent_id:
                print(f"  Warning: parent '{data['parent_name']}' not found for '{data['name']}'")
                continue
            genre = Genre(
                name=data["name"],
                parent_id=parent_id,
                description=data.get("description"),
                bpm_min=data.get("bpm_min"),
                bpm_max=data.get("bpm_max"),
                common_keys=data.get("common_keys", []),
                common_instruments=data.get("common_instruments", []),
                production_techniques=data.get("production_techniques", []),
                vocal_style=data.get("vocal_style"),
                sources=["Sonmancer Seed Data"],
            )
            db.add(genre)
        db.commit()

        total = db.query(Genre).count()
        print(f"✅ Seeded {total} genres successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_genres()
