
from backend.database import SessionLocal
from backend.models import Announcement

db = SessionLocal()
new_announcement = Announcement(
    title="Portal Notice",
    message="Remember that you can now check active support ticket threads and export chat transcripts directly from the header!",
    is_active=True
)
db.add(new_announcement)
db.commit()
db.close()
print("Test announcement added successfully!")