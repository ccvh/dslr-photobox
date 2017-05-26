var express = require('express');
var app = express();

var Gallery = require('express-photo-gallery');

var options = {
  title: 'OldGents Photobox Gallery'
};

app.use('/', Gallery('/home/pi/photobox/images', options));

app.listen(80);
