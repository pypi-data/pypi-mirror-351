# Progression Picture Pal
PPP is _perfect_ if you want to automate showing progression in images.

## Examples
All images generated with the below code with different `num_images` and `max_per_row` values to show different behaviour

```python
def create_flow_diagram(images, output_path, num_images=None, **fd_kwargs):
    """
    Generate and save a flow diagram from a list of (image_path, caption) tuples.

    :param images: List of (image_path, caption) tuples.
    :param output_path: File path to save the resulting diagram.
    :param num_images: Number of images from the list to include (default: all).
    :param fd_kwargs: Keyword args passed to FlowDiagram initializer.
    """
    if num_images is None:
        num_images = len(images)
    fd = FlowDiagram(**fd_kwargs)
    for image_path, caption in images[:num_images]:
        fd.add_node(image_path, caption)
    for i in range(min(num_images, len(images)) - 1):
        fd.add_arrow(i, i+1)
    fd.save(output_path)


images = [
    ("example_images/step1.JPG", "\"First you go to the beach\""),
    ("example_images/step2.JPG", "\"Then you look at a green bush and think about your place in the world\""),
    ("example_images/step3.JPG", "\"Then you see a red leaf\""),
    ("example_images/step4.JPG", "\"But then you see a white house\""),
    ("example_images/step5.JPG", "\"So you look at some bins\""),
    ("example_images/step6.JPG", "\"And then some more houses\""),
    ("example_images/step7.JPG", "\"Before finally looking at your foot\""),
]

create_flow_diagram(
    images=images,
    output_path="flow_output.png",
    num_images=6,
    spacing=160,
    spacing_vertical=100,
    max_node_dim=400,
    max_per_row=3,
    font_size=20,
    arrow_padding_v=70
)
```

### Basic
```python
num_images=3
```

![](examples/3_in_a_row.png)

### Wrapping with even
```python
num_images=7
```
![](examples/4_with_7.png)


### Wrapping with odd
```python
num_images=6 
max_per_row=3
```
![](examples/3_with_6.png)

# Sponsorship
Sample images kindly provided by Sam Lewis of https://snaps.samlewis.me .