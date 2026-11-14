"""V22: short visual QC of one white-sneaker walk and one clearly visible puddle.
Does not synthesize or assemble any videos.
"""
import v18_pexels_review as q
q.VIDEOS=[
 {"id":"walk_white","page":"https://www.pexels.com/video/a-person-wearing-white-sneakers-standing-on-the-road-25956625/","download":"https://www.pexels.com/download/video/25956625/","expected_duration":10},
 {"id":"rain_visible","page":"https://www.pexels.com/video/rainfall-over-puddle-13749224/","download":"https://www.pexels.com/download/video/13749224/","expected_duration":32}
]
if __name__=="__main__":q.main()
