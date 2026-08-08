from app.evidence.hashing import hash_file, hash_bytes

# Hash some in-memory bytes first, to confirm the basic function works
sample = b"hello ppe monitoring"
print("hash_bytes result:", hash_bytes(sample))

# Confirm hashing the same bytes twice gives the same result (hashes must be deterministic)
print("Same input, same hash:", hash_bytes(sample) == hash_bytes(sample))

# Confirm different bytes give a different hash
print("Different input, different hash:", hash_bytes(sample) != hash_bytes(b"different data"))

# Write a small real file and hash it with hash_file, to test the file-reading path
with open("test_evidence_file.txt", "wb") as f:
    f.write(sample)
print("hash_file result:", hash_file("test_evidence_file.txt"))
print("hash_file matches hash_bytes:", hash_file("test_evidence_file.txt") == hash_bytes(sample))