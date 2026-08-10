from app import config

print("PROJECT_ROOT:", config.PROJECT_ROOT)
print("DATABASE_PATH:", config.DATABASE_PATH)
print("MODEL_PATH:", config.MODEL_PATH)
print("EVIDENCE_ROOT:", config.EVIDENCE_ROOT)
print("Database file exists:", (config.PROJECT_ROOT / "violations.db").exists())
print("Model file exists:", Path(config.MODEL_PATH).exists() if (Path := __import__("pathlib").Path) else None)