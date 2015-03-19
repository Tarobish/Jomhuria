# Jomhuria font project

A persian/arabic and latin fat display font.



### Building

#### Preparations

The build process that we took over from [Amiri](http://www.amirifont.org/) can be executed from
the Dockerfile located in the directory `tools/docker_fontbuilder/`. This in turn depends on the Docker
image debian/sortsmill: https://github.com/graphicore/docker-sortsmill

When `debian/sortsmill` is available you can make `debian/fontbuilder`:

```
$ cd tools/docker_fontbuilder
$ sudo docker build -t debian/fontbuilder .

```

Alternatively you can use the Dockerfiles to find out about the dependencies of this package.


#### Building with Docker


```
# make the font files and all webfont files in the generated directory
$ sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && make"; sudo chown -R $USER:$USER .

# run the testsuite (make check)
sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && make check"; sudo chown -R $USER:$USER .

# create documentation pdfs in the documentation directory
sudo docker run -v `pwd`:/var/job debian/fontbuilder /bin/sh -c "cd /var/job && make doc"; sudo chown -R $USER:$USER .

```

