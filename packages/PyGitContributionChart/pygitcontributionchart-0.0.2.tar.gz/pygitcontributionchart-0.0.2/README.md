# GitCommitChart

This is a small python library that uses PIL to generate Github commit charts dynamically. Its very cool.

## Examples

Create a simple chart
```py
from GitCommitChart import create_git_commit_chart
import random

if __name__ == "__main__":
    # Example data array with 365 elements
    # each with a random value between 0 and 100
    data = [random.randint(0, 10) for i in range(365)] 


    # Create the Git commit chart
    image = create_git_commit_chart(data, rows_per_column=7)
    image.save("test.png")
```
![alt text](docs/image-1.png)

Create a chart with labels
```py
from GitCommitChart import create_git_commit_chart
import random

if __name__ == "__main__":
    data = [random.randint(0, 10)
            for i in range(365)]  # Example data for a year

    # Create the Git commit chart
    image = create_git_commit_chart(
        data,
        rows_per_column=7,
        horizontal_labels=["Jan", "Feb", "Mar"...
        vertical_labels=["Sun", "Wed", "Sat"],
        label_font_size=40
    )
    image.save("test.png")

```
![alt text](docs/image-2.png)