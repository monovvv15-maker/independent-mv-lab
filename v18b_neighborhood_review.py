"""V18B: same bounded tool on two alternative neighborhood clips only."""
import v18_pexels_review as pipeline
pipeline.VIDEOS=[
 {"id":"tree_street","page":"https://www.pexels.com/video/quiet-urban-street-scene-with-lush-trees-34381897/","download":"https://www.pexels.com/download/video/34381897/","expected_duration":9},
 {"id":"suburb_spring","page":"https://www.pexels.com/video/quiet-suburban-neighborhood-in-spring-40456181/","download":"https://www.pexels.com/download/video/40456181/","expected_duration":21}
]
if __name__=="__main__":
    pipeline.main()
