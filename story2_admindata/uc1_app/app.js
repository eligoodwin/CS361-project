// Story 2, use case 1. Admin should see list of inmates.

// The following setting were adapted from the CS290 lectures

var express = require('express');
var app = express();
var handlebars = require('express-handlebars').create({defaultLayout:'main'});
var bodyParser = require('body-parser');
var request = require('request');

// Grab the database configuration
var mysql = require('../../database/dbcon.js');

app.engine('handlebars', handlebars.engine);
app.set('view engine', 'handlebars');
app.set('port', process.argv[2]);
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static(__dirname + '/public'));

app.get('/', function(req, res, next){
        var context = {};
        context.data = {};
        mysql.pool.query("SELECT * FROM inmate",  function(err, rows, fields){
            if(err){
              next(err);
              return;
            }
            context.data = rows;
            console.log(context.data)
            //res.render('inmateLista', context);
        });
    });

app.use(function(req,res){
  res.status(404);
  res.render('404');
});

app.use(function(err, req, res, next){
  console.error(err.stack);
  res.type('plain/text');
  res.status(500);
  res.render('500');
});


app.listen(app.get('port'), function(){
  console.log('Express started on port ' + app.get('port') + '; press Ctrl-C to terminate.');
});


