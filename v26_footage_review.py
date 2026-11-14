"""V26 optional real-footage sample QA, no MV video is assembled."""
import json
import v18_pexels_review as r
catalog=json.load(open("catalog/v26_full_length_candidates.json",encoding="utf-8"))["items"]
sample_ids={35608286,3968496,37108132,10695941,34506423,37541865,31432212,12769743}
r.VIDEOS=[{"id":str(c["id"]),"page":c["url"],"download":c["download_url"],"expected_duration":c["duration"] or 9} for c in catalog if c["id"] in sample_ids]
if __name__=="__main__":
    r.main()
