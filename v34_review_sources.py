"""V34 verify missing story-action video clips by frames. No MV rendered."""
import json
import v18_pexels_review as review
from pathlib import Path
data=json.loads(Path("catalog/v34_targeted_footage_candidates.json").read_text(encoding="utf-8"))
review.VIDEOS=[
 {"id":str(row["id"]),"page":row["url"],"download":f'https://www.pexels.com/download/video/{row["id"]}/',"expected_duration":8}
 for row in data["candidates"]
]
if __name__=="__main__":
 review.main()
