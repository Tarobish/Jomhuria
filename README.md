# Jomhuria font project

Jomhuria is a dark Persian/Arabic and Latin display typeface, suitable for headline and other display usage. 

The name means 'republic,' and the spark of inspiration for the design was a stencil of “Shablon” showing just a limited character set just for the Persian language without any marks, vowels or Latin glyphs.
Shablon was designed 30 years ago in Iran, and is reinterpreted by Kourosh to incorporate contemporary techniques, aesthetics and of course some personal taste. 
While inspired by the spirit of Shablon, Jomhuria is a new typeface that stands on its own.
Kourosh created an additional original Latin design that is tailored to harmonize with the aesthetics of the Persian/Arabic design.

Being made for big sizes means details matter. 
The positions of the dots remains faithful to their locations in Persian/Arabic calligraphy; 
this is an important factor of beauty in the writing system and is key to readability.

The Arabic script was designed by Kourosh Beigpour, and the Latin was designed by Eben Sorkin. 
The font is engineered by Lasse Fister, and the technicalities build upon those developed by Khaled Hosny for his “Amiri.”

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

