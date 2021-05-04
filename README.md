# land_use
Predicting future land use in Auckland using Python


### Installation

`sudo pip3 install -r requirements.txt`

### Running

`jupyter-notebook preprocess.ipynb`

### Running with docker

```docker
docker run --rm --volume `pwd`:/app --publish 8888:8888 uoacer/land_use
```

### Notebooks

These Python Jupyter (.ipynb) notebooks have been converted to HTML with `jupyter-nbconvert --to html preprocess.ipynb` for ease of viewing results

- [preprocess](https://uoa-eresearch.github.io/land_use/preprocess)
- [predict](https://uoa-eresearch.github.io/land_use/predict)

### Output GIFs

![land_use.gif](land_use.gif)
![pop.gif](pop.gif)
