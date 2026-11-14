"""V21: inspect six visually coherent candidate clips before video rendering.
This workflow downloads only Pexels Free Download URLs explicitly listed by the provider.
Existing MP4s are kept ephemeral and never uploaded into GitHub or published as artifacts.
"""
import v18_pexels_review as review

review.VIDEOS=[
 {"id":"intro_neighborhood","page":"https://www.pexels.com/video/quiet-suburban-neighborhood-in-spring-40456181/","download":"https://www.pexels.com/download/video/40456181/","expected_duration":21},
 {"id":"rain_puddle","page":"https://www.pexels.com/video/rain-ripples-3986759/","download":"https://www.pexels.com/download/video/3986759/","expected_duration":30},
 {"id":"shoes_indoor","page":"https://www.pexels.com/video/low-angle-view-of-a-person-putting-on-the-shoe-and-tying-it-4953053/","download":"https://www.pexels.com/download/video/4953053/","expected_duration":9},
 {"id":"walking","page":"https://www.pexels.com/video/footage-of-a-person-walking-5571491/","download":"https://www.pexels.com/download/video/5571491/","expected_duration":12},
 {"id":"window","page":"https://www.pexels.com/video/a-person-opening-a-window-5835695/","download":"https://www.pexels.com/download/video/5835695/","expected_duration":9},
 {"id":"neighborhood_outro","page":"https://www.pexels.com/video/quiet-urban-street-scene-with-lush-trees-34381897/","download":"https://www.pexels.com/download/video/34381897/","expected_duration":9},
]
if __name__=="__main__":
    review.main()
